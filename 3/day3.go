package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"regexp"
	"sort"
	"strconv"
)

type Input struct {
	multiplications []MultiplicationInput
	disabledRanges  [][]int
}

type MultiplicationInput struct {
	a     int
	b     int
	index int
}

type EnableDisableCommand struct {
	begin  int
	end    int
	enable bool
}

type CommandsByRange []EnableDisableCommand

func (c CommandsByRange) Len() int           { return len(c) }
func (c CommandsByRange) Less(i, j int) bool { return c[i].begin < c[j].begin }
func (c CommandsByRange) Swap(i, j int)      { c[i], c[j] = c[j], c[i] }

func calculateDisabledRanges(input string) [][]int {
	doRegex := regexp.MustCompile(`do\(\)`)
	dontRegex := regexp.MustCompile(`don't\(\)`)

	doIndices := doRegex.FindAllStringIndex(input, -1)
	dontIndices := dontRegex.FindAllStringIndex(input, -1)

	commands := []EnableDisableCommand{}
	for _, doIndex := range doIndices {
		cmd := EnableDisableCommand{
			begin:  doIndex[0],
			end:    doIndex[1],
			enable: true,
		}

		commands = append(commands, cmd)
	}

	for _, dontIndex := range dontIndices {
		cmd := EnableDisableCommand{
			begin:  dontIndex[0],
			end:    dontIndex[1],
			enable: false,
		}

		commands = append(commands, cmd)
	}

	sort.Sort(CommandsByRange(commands))

	invalidRanges := make([][]int, 0)
	isDisabled := false
	currentDisabledRangeBegin := -1
	for _, cmd := range commands {
		// This basically means we need to start a disabled range
		if !isDisabled && !cmd.enable {
			isDisabled = true
			currentDisabledRangeBegin = cmd.end
		}

		// We need to end the disabled range
		if isDisabled && cmd.enable {
			isDisabled = false
			invalidRanges = append(invalidRanges, []int{currentDisabledRangeBegin, cmd.end})
			currentDisabledRangeBegin = -1
		}
	}

	if isDisabled && currentDisabledRangeBegin != -1 {
		invalidRanges = append(invalidRanges, []int{currentDisabledRangeBegin, len(input)})
	}

	return invalidRanges
}

func indexInDisabledRange(disabledRanges [][]int, i int) bool {
	for _, r := range disabledRanges {
		if i >= r[0] && i <= r[1] {
			return true
		}
	}

	return false
}

func readInput(inputFile string) (*Input, error) {
	file, err := os.Open(inputFile)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	b, err := io.ReadAll(file)
	if err != nil {
		return nil, err
	}

	inputString := string(b)

	input := &Input{
		multiplications: make([]MultiplicationInput, 0),
		disabledRanges:  calculateDisabledRanges(inputString),
	}

	mulRegex := regexp.MustCompile(`mul\((\d{1,3}),(\d{1,3})\)`)

	matches := mulRegex.FindAllStringSubmatchIndex(inputString, -1)

	for _, matches := range matches {
		if len(matches) != 6 {
			return nil, errors.New("Invalid match length")
		}

		a, err := strconv.Atoi(inputString[matches[2]:matches[3]])
		if err != nil {
			return nil, err
		}

		b, err := strconv.Atoi(inputString[matches[4]:matches[5]])
		if err != nil {
			return nil, err
		}

		mult := MultiplicationInput{
			a:     a,
			b:     b,
			index: matches[0],
		}

		input.multiplications = append(input.multiplications, mult)
	}
	return input, nil

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

	sum := 0
	for _, mult := range input.multiplications {
		sum += mult.a * mult.b
	}

	fmt.Println("Multiplication product sum is", sum)

	sum = 0
	for _, mult := range input.multiplications {
		if indexInDisabledRange(input.disabledRanges, mult.index) {
			//fmt.Println("Skipping match", begin, "in disabled range")
			continue
		} else {
			sum += mult.a * mult.b
		}
	}

	fmt.Println("Multiplication sum with enable/disable is", sum)

}
