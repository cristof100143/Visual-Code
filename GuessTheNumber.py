import random

def guess_the_number():
    number_to_guess = random.randint(1, 100)
    number_of_guesses = 0
    print("Welcome to 'Guess the Number' game!")
    print("I'm thinking of a number between 1 and 100.")

    while True:
        user_guess = int(input("Take a guess: "))
        number_of_guesses += 1

        if user_guess < number_to_guess:
            print("Your guess is too low.")
        elif user_guess > number_to_guess:
            print("Your guess is too high.")
        else:
            print(f"Congratulations! You guessed the number in {number_of_guesses} tries.")
            break

guess_the_number()
