def calculate(a, operator, b):
    if operator == "sum":
        return a + b
    elif operator == "subtract":
        return a - b
    elif operator == "multiply":
        return a * b
    elif operator == "divide":
        if b != 0:
            return a / b
        else:
            print("Error: Division by zero is not allowed.")
            return None

def main():
    while True:
        command = input("Enter one of the following commands:\n1. sum\n2. subtract\n3. multiply\n4. divide\n").strip().lower()
        
        if command == "sum" or command == "subtract" or command == "multiply" or command == "divide":
            break
        else:
            print("Invalid command. Please try again.")
    
    while True:
        a = float(input("Enter value A: "))
        b = input("Enter operator (+, -, *, /): ").strip().lower()
        
        if b in ["+", "-", "*", "/"]:
            break
        else:
            print("Invalid operator. Please try again.")
    
    result = calculate(a, b, float(input(f"Enter value B: ")))
    if result is not None:
        print(f"{a} {b} {b} = {result}")

if __name__ == "__main__":
    main()