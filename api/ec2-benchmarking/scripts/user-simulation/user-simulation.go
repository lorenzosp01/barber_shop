package main

import (
	"ec2-benchmarking/lib"
	"fmt"
	"time"
)

const parallelUsers = 20

func main() {
	// A single instance of the script runs 20 users
	users := make([]*lib.UserSimulation, parallelUsers)
	for i := 0; i < parallelUsers; i++ {
		users[i] = lib.NewUserSimulation("losp0401@gmail.com", "Lorenzo01@")
	}

	// Start the user simulations, in background
	for i := 0; i < parallelUsers; i++ {
		go users[i].Run()
	}

	// Every minute, we want to collect statistics and print them
	for {
		// Wait
		time.Sleep(60 * time.Second)

		// Get the current time, as HH:MM:SS
		currentTime := time.Now().Format("15:04:05")

		// Collect statistics
		for i := 0; i < parallelUsers; i++ {
			statistics := users[i].ResetStatistics()

			// Print a single line as:
			// [currentTime] User [i] - ValidRequests: 0, FailedRequests: 0, TimeMean: 0.0, TimeStdDev: 0.0,
			fmt.Printf("[%s] User %d: ValidRequests: %d, FailedRequests: %d, TimeMean: %.1f, TimeStdDev: %.1f,\n",
				currentTime, i, statistics.ValidRequests, statistics.FailedRequests, statistics.TimeMean, statistics.TimeStdDev)
		}
	}
}
