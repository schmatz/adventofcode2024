package main

import (
	"bufio"
	"errors"
	"flag"
	"fmt"
	"log"
	"math"
	"os"
	"regexp"
	"slices"
	"strconv"
)

type Input struct {
	listOne []int
	listTwo []int
}

var inputFileRegex = regexp.MustCompile(`(?P<first>\d+)\s+(?P<second>\d+)`)

func readInput(inputFile string) (*Input, error) {
	file, err := os.Open(inputFile)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	input := &Input{}
	input.listOne = make([]int, 0, 1000)
	input.listTwo = make([]int, 0, 1000)

	for scanner.Scan() {
		matches := inputFileRegex.FindStringSubmatch(scanner.Text())
		firstIndex := inputFileRegex.SubexpIndex("first")
		secondIndex := inputFileRegex.SubexpIndex("second")

		firstNumber, err := strconv.Atoi(matches[firstIndex])
		if err != nil {
			log.Fatal(err)
		}
		secondNumber, err := strconv.Atoi(matches[secondIndex])
		if err != nil {
			log.Fatal(err)
		}
		input.listOne = append(input.listOne, firstNumber)
		input.listTwo = append(input.listTwo, secondNumber)
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	return input, nil

}

func calculateDistance(a []int, b []int) (distance int, err error) {
	if len(a) != len(b) {
		return 0, errors.New("Lists are not same length")
	}

	slices.Sort(a)
	slices.Sort(b)

	distance = 0
	for i := 0; i < len(a); i++ {
		distance += int(math.Abs(float64(a[i] - b[i])))
	}

	return distance, nil
}

func calculateSimilarityScore(left []int, right []int) (similarity int, err error) {
	rightFrequencies := make(map[int]int)
	for i := 0; i < len(right); i++ {
		elem := right[i]
		rightFrequencies[elem] += 1
	}

	similarity = 0
	for i := 0; i < len(left); i++ {
		elem := left[i]
		freq, ok := rightFrequencies[elem]
		if !ok {
			continue
		}

		similarity += elem * freq
	}

	return similarity, nil

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

	dist, err := calculateDistance(input.listOne, input.listTwo)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Distance is", dist)
	similarity, err := calculateSimilarityScore(input.listOne, input.listTwo)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Similarity is", similarity)
}
