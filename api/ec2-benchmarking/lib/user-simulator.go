package lib

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"os"
	"sync"
	"time"
)

type UserSimulation struct {
	username       string
	password       string
	currentState   string
	token          string
	durationsMutex sync.Mutex
	durations      []int
	failedRequests int
}

type UserSimulationStats struct {
	ValidRequests  int
	FailedRequests int
	TimeMean       float64
	TimeStdDev     float64
}

const startState = "start"
func NewUserSimulation(username string, password string) *UserSimulation {

	return &UserSimulation{
		currentState:   startState,
		username:       username,
		password:       password,
		durationsMutex: sync.Mutex{},
		durations:      []int{},
		failedRequests: 0,
	}
}

const debugLog = false

func log(args ...any) {
	if debugLog {
		fmt.Println(args...)
	}
}


const uploadReviewState = "uploadReview"
const listPersonalReviewsState = "listPersonalReviews"
const listAllReviewsState = "listAllReviews"

func (u *UserSimulation) login() error {
	log("Logging in...")

	payload := Payload{
		username: u.username,
		password: u.password,
	}
	body, duration, err := timeHTTPPost("/auth/get-token", payload, "")
	if err != nil {
		return err
	}

	u.collectDuration(duration)
	// Parse the response to get the token
	// The response is a JSON object with a key "token"
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(body), &data); err != nil {
		log("Error: login JSON is not valid")
		return err
	}

	u.token = data["access_token"].(string)

	return nil

}
func (u *UserSimulation) start() string {
	log("Entering start state...")

	if u.token == "" {
		err := u.login()
		if err != nil {
			log("Error: login failed")
			return startState
		}
	}
	next := rand.Float32()
	if next < 0.1 {
		// 10%
		return uploadReviewState
	}
	if next < 0.3 {
		// 20%
		return listPersonalReviewsState
	}
	// 70%
	return listAllReviewsState
}

func (u *UserSimulation) listPersonalReviews() string {
	log("Entering listReviews state...")

	_, duration, err := timeHTTPRequest("/api/list-user-reviews", true, u.token)
	if err != nil {
		// Failure!
		u.collectDuration(-1)
		return startState
	}

	u.collectDuration(duration)

	return startState
}

func (u *UserSimulation) listAllReviews() string {
	_, duration, err := timeHTTPRequest("/api/list-reviews", true, "")
	if err != nil {
		// Failure!
		u.collectDuration(-1)
		return startState
	}

	u.collectDuration(duration)

	return startState
}

func (u *UserSimulation) uploadReview() string {
	log("Entering uploadPhoto state...")

	// List all files in ./test-assets
	assetsPhotos, err := os.ReadDir("./test-assets")
	if err != nil {
		panic(err) // Totally fine to panic here, as this is a developer error
	}

	// Pick a random photo
	photoToUpload := assetsPhotos[rand.Intn(len(assetsPhotos))].Name()
	photoPath := fmt.Sprintf("./test-assets/%s", photoToUpload)
	payload := Payload{
		title:   "Test title",
		content: "Test content",
		rating:  5,
	}
	body, duration, err := timeHTTPPostFile("/api/upload-review", payload, photoPath, photoToUpload, u.token)
	if err != nil {
		// Failure!
		u.collectDuration(-1)
		return startState
	}

	u.collectDuration(duration)

	// Parse the response to get the photo ID
	// The response is a JSON object with a key "photo_id"
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(body), &data); err != nil {
		log("Error: uploadPhoto JSON is not valid")
		return startState
	}

	return startState
}

func (u *UserSimulation) Run() {
	for {
		nextState := ""
		switch u.currentState {
		case startState:
			nextState = u.start()
		case uploadReviewState:
			nextState = u.uploadReview()
		case listAllReviewsState:
			nextState = u.listAllReviews()
		case listPersonalReviewsState:
			nextState = u.listPersonalReviews()
		}

		var lastRequestTime int
		u.durationsMutex.Lock()
		if len(u.durations) > 0 {
			lastRequestTime = u.durations[len(u.durations)-1]
		} else {
			lastRequestTime = 0
		}
		u.durationsMutex.Unlock()

		if nextState != startState && lastRequestTime > -1 {
			// Wait 1 second before transitioning to the next state,
			// to simulate a user thinking about what to do next,
			// except when going back to the start state.
			//
			// Also, do not wait if the last request failed,
			// since we need to stress test the system.
			time.Sleep(1 * time.Second)
		}
		u.currentState = nextState
	}
}

func (u *UserSimulation) collectHTTPRequestWithBody(url string) (string, error) {
	body, duration, err := TimeHTTPRequestWithBody(url)
	if err != nil {
		u.collectDuration(-1)
	} else {
		u.collectDuration(duration)
	}
	return body, err
}

func (u *UserSimulation) collectHTTPRequest(url string) error {
	// Do not reuse collectHTTPRequestWithBody, as we don't need the body,
	// and we do not even want to read it from the response stream connection.
	duration, err := TimeHTTPRequest(url)
	if err != nil {
		u.collectDuration(-1)
	} else {
		u.collectDuration(duration)
	}
	return err
}

func (u *UserSimulation) collectDuration(duration int) {
	u.durationsMutex.Lock()
	defer u.durationsMutex.Unlock()

	log("Collecting duration", duration)

	if duration == -1 {
		u.failedRequests++
	} else {
		u.durations = append(u.durations, duration)
	}
}

func (u *UserSimulation) ResetStatistics() UserSimulationStats {
	u.durationsMutex.Lock()
	defer u.durationsMutex.Unlock()

	// Compute the mean
	var sum int
	for _, d := range u.durations {
		sum += d
	}
	mean := float64(sum) / float64(len(u.durations))

	// Compute the standard deviation
	var sumSquaredDiff float64
	for _, d := range u.durations {
		diff := float64(d) - mean
		sumSquaredDiff += diff * diff
	}
	stdDev := math.Sqrt(sumSquaredDiff / float64(len(u.durations)))

	stats := UserSimulationStats{
		ValidRequests:  len(u.durations),
		FailedRequests: u.failedRequests,
		TimeMean:       mean,
		TimeStdDev:     stdDev,
	}

	// Reset the accumulated durations
	u.durations = []int{}
	u.failedRequests = 0

	return stats
}
