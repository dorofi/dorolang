class TemplateManager:
    """Code template manager"""
    
    @staticmethod
    def get_templates():
        """Returns dictionary of available templates"""
        return {
            "Hello World": '''# Hello World in DoroLang
say "Hello, DoroLang!"
say "Welcome to the world of programming!"''',
            
            "Variables": '''# Working with variables
kas name = "Your name"
kas age = 25
kas is_student = true

say "Name: " + name
say "Age: " + age
say "Student: " + is_student''',
            
            "Conditional Logic": '''# Conditional logic
kas score = 85
kas passed = score >= 60

if (passed) {
    say "Congratulations! You passed the test!"
    kas grade = "Pass"
} else {
    say "Unfortunately, the test was not passed"
    kas grade = "Fail"
}

say "Final grade: " + grade''',
            
            "Complex Logic": '''# Complex logic
kas temperature = 22
kas is_sunny = true
kas is_weekend = false

kas good_weather = temperature > 20 and is_sunny
kas can_go_out = good_weather and (is_weekend or temperature > 25)

if (can_go_out) {
    say "Great weather for a walk!"
} else {
    if (not good_weather) {
        say "Weather is not very good"
    } else {
        say "Weather is good, but today is a workday"
    }
}''',
            
            "Calculator": '''# Simple calculator
kas a = 15
kas b = 7

say "Number A: " + a
say "Number B: " + b
say "Sum: " + (a + b)
say "Difference: " + (a - b)
say "Product: " + (a * b)
say "Quotient: " + (a / b)
say "Remainder: " + (a % b)

# Comparisons
say "A greater than B: " + (a > b)
say "A equals B: " + (a == b)
say "A not equal to B: " + (a != b)''',
            
            "Input Example": '''# Interactive input example
kas name = input("What is your name? ")
kas age = input("How old are you? ")

say "Hello, " + name + "!"
say "You are " + age + " years old"

kas age_num = age
if (age_num >= 18) {
    say "You are an adult"
} else {
    say "You are a minor"
}''',
            
            "Nested Conditionals": '''# Nested if-else example
kas score = 85
kas attendance = 90

if (score >= 90) {
    if (attendance >= 90) {
        say "Excellent! Grade: A+"
    } else {
        say "Good score! Grade: A"
    }
} else {
    if (score >= 80) {
        say "Good work! Grade: B"
    } else {
        if (score >= 70) {
            say "Passing grade: C"
        } else {
            say "Needs improvement: D"
        }
    }
}''',
            
            "Logical Operators": '''# Logical operators demonstration
kas x = 10
kas y = 5
kas z = 15

kas result1 = x > y and x < z
kas result2 = x < y or z > x
kas result3 = not (x == y)

say "x > y and x < z: " + result1
say "x < y or z > x: " + result2
say "not (x == y): " + result3

if (result1 and result2) {
    say "Both conditions are true!"
}

if (result1 or result3) {
    say "At least one condition is true"
}''',
            
            "String Operations": '''# String operations
kas first_name = "John"
kas last_name = "Doe"
kas full_name = first_name + " " + last_name

say "First name: " + first_name
say "Last name: " + last_name
say "Full name: " + full_name

kas greeting = "Hello, " + full_name + "!"
say greeting

kas age = 25
kas info = full_name + " is " + age + " years old"
say info''',
            
            "While Loop": '''# While loop example
kas counter = 1

while (counter <= 5) {
    say "Count: " + counter
    kas counter = counter + 1
}

say "Loop finished!"''',
            
            "For Loop": '''# For loop example
say "Counting from 1 to 10:"

for kas i = 1 to 10 {
    say "Number: " + i
}

say "Counting backwards:"
for kas j = 10 to 1 step -1 {
    say "Number: " + j
}''',
            
            "Nested Loops": '''# Nested loops example
say "Multiplication table:"

for kas i = 1 to 5 {
    for kas j = 1 to 5 {
        kas result = i * j
        say i + " x " + j + " = " + result
    }
    say "---"
}''',
            
            "Loop with Conditionals": '''# Loops with conditionals
say "Even numbers from 1 to 20:"

for kas i = 1 to 20 {
    kas remainder = i % 2
    if (remainder == 0) {
        say i + " is even"
    }
}

say "Numbers divisible by 3:"
kas num = 1
while (num <= 30) {
    if (num % 3 == 0) {
        say num + " is divisible by 3"
    }
    kas num = num + 1
}''',
            
            "Simple Function": '''# Simple function example
function greet(name) {
    return "Hello, " + name + "!"
}

say greet("Alice")
say greet("Bob")
say greet("Charlie")''',
            
            "Function with Parameters": '''# Function with multiple parameters
function add(a, b) {
    return a + b
}

function multiply(x, y) {
    return x * y
}

say "5 + 3 = " + add(5, 3)
say "4 * 7 = " + multiply(4, 7)
say "10 + 20 = " + add(10, 20)''',
            
            "Function with Conditionals": '''# Function using conditionals
function max(a, b) {
    if (a > b) {
        return a
    } else {
        return b
    }
}

function min(x, y) {
    if (x < y) {
        return x
    } else {
        return y
    }
}

say "Max of 10 and 5: " + max(10, 5)
say "Min of 10 and 5: " + min(10, 5)''',
            
            "Recursive Function": '''# Recursive function - factorial
function factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

say "Factorial of 5: " + factorial(5)
say "Factorial of 7: " + factorial(7)''',
            
            "Function with Loops": '''# Function using loops
function count_to_n(n) {
    for kas i = 1 to n {
        say i
    }
}

function sum_numbers(n) {
    kas total = 0
    for kas i = 1 to n {
        kas total = total + i
    }
    return total
}

count_to_n(5)
say "Sum of 1 to 10: " + sum_numbers(10)''',
            
            "Complete Program": '''# Complete program using all features
function calculate_grade(score) {
    if (score >= 90) {
        return "A"
    } else {
        if (score >= 80) {
            return "B"
        } else {
            if (score >= 70) {
                return "C"
            } else {
                return "F"
            }
        }
    }
}

function print_grades() {
    say "Student Grades:"
    for kas i = 1 to 5 {
        kas score = 60 + (i * 8)
        kas grade = calculate_grade(score)
        say "Student " + i + ": Score " + score + " = Grade " + grade
    }
}

print_grades()''',
            
            "Interactive Function": '''# Interactive program with functions
function greet_user(name, age) {
    kas greeting = "Hello, " + name + "! You are " + age + " years old."
    return greeting
}

kas user_name = input("Enter your name: ")
kas user_age = input("Enter your age: ")

say greet_user(user_name, user_age)

if (user_age >= 18) {
    say "You are an adult"
} else {
    say "You are a minor"
}''',
            
            "Calculator Functions": '''# Calculator using functions
function add(a, b) {
    return a + b
}

function subtract(a, b) {
    return a - b
}

function multiply(a, b) {
    return a * b
}

function divide(a, b) {
    return a / b
}

say "10 + 5 = " + add(10, 5)
say "10 - 5 = " + subtract(10, 5)
say "10 * 5 = " + multiply(10, 5)
say "10 / 5 = " + divide(10, 5)''',
            
            "Function Examples": '''# Multiple function examples
function is_even(n) {
    kas remainder = n % 2
    return remainder == 0
}

function is_positive(x) {
    return x > 0
}

function power(base, exponent) {
    kas result = 1
    for kas i = 1 to exponent {
        kas result = result * base
    }
    return result
}

say "Is 8 even? " + is_even(8)
say "Is 7 even? " + is_even(7)
say "Is 5 positive? " + is_positive(5)
say "2 to the power of 3: " + power(2, 3)'''
        }

