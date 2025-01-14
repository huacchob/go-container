package main

import (
	"fmt"
	"regexp"
)

func findMatch(exp string, str string) string {
	re, _ := regexp.Compile(exp)
	matched := re.FindString(str)
	return matched
}

func main() {
	var str string
	var exp string
	str = "Peach and peaches"
	exp = "P\\S+h"
	fmt.Println(findMatch(exp, str))
}
