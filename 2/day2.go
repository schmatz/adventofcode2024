package main

import (
	"bufio"
	"flag"
	"fmt"
	"log"
	"math"
	"os"
	"regexp"
	"strconv"
)

type Input struct {
	reports [][]int
}

func readInput(inputFile string) (*Input, error) {
	file, err := os.Open(inputFile)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	input := &Input{}
	input.reports = make([][]int, 0, 1000)

	for scanner.Scan() {
		line := scanner.Text()

		numberRegex := regexp.MustCompile(`\d+`)
		matches := numberRegex.FindAllString(line, -1)

		report := make([]int, 0, 10)

		for _, match := range matches {
			num, err := strconv.Atoi(match)
			if err != nil {
				return input, err
			}

			report = append(report, num)
		}

		input.reports = append(input.reports, report)
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	return input, nil

}

func isPairSafe(a int, b int, increasing bool) bool {
	diff := int(math.Abs(float64(a - b)))
	if diff > MAX_SAFE_DIST || diff < 1 {
		return false
	}

	if (b < a && increasing) || (b > a && !increasing) {
		return false
	}

	return true
}

func calculateIsReportSafe(report []int) bool {
	if len(report) < 2 {
		log.Fatal("Violations around length assumptions")
	}
	increasing := report[1] > report[0]

	for i := 0; i < len(report)-1; i++ {
		a := report[i]
		b := report[i+1]

		isSafe := isPairSafe(a, b, increasing)
		if !isSafe {
			return false
		}
	}

	return true
}

const MAX_SAFE_DIST = 3

func calculateSafeReports(reports [][]int, margin bool) int {
	safeReports := 0
	for _, report := range reports {
		isSafe := calculateIsReportSafe(report)
		if isSafe {
			safeReports += 1
			fmt.Println("report is safe", report)
		} else {
			if margin {
				for i := 0; i < len(report); i++ {
					reportCopy := make([]int, len(report))
					copy(reportCopy, report)

					spliced := append(reportCopy[:i], reportCopy[i+1:]...)
					if calculateIsReportSafe(spliced) {
						fmt.Println("Report was made safe by removing", i, report)
						safeReports += 1
						break
					}
				}
			}
		}

	}

	return safeReports
}

func main() {
	var inputFile string
	flag.StringVar(&inputFile, "file", "", "Path to the input file")
	flag.StringVar(&inputFile, "f", "", "Path to the input file (shorthand)")
	flag.Parse()

	if inputFile == "" {
		fmt.Println("Please provide an input file using -file or -f flag")
		flag.Usage()
		os.Exit(1)
	}

	fmt.Printf("Reading from file: %s\n", inputFile)

	input, err := readInput(inputFile)
	if err != nil {
		log.Fatal(err)
	}

	safeReports := calculateSafeReports(input.reports, false)
	log.Println("Safe reports are", safeReports)

	safeReportsWithMargin := calculateSafeReports(input.reports, true)

	log.Println("Safe reports with margin are", safeReportsWithMargin)

}
