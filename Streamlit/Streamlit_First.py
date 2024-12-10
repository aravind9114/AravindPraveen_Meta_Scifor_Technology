import streamlit as st
st.title("Calculator")
num1 = st.number_input("Enter first number", step=1.0)
num2 = st.number_input("Enter second number", step=1.0)
operation = st.selectbox("Select operation", ["Add", "Subtract", "Multiply", "Divide"])
if st.button("Calculate"):
    if operation == "Add":
        result = num1 + num2
        st.write(f"Result: {num1} + {num2} = {result}")
    elif operation == "Subtract":
        result = num1 - num2
        st.write(f"Result: {num1} - {num2} = {result}")
    elif operation == "Multiply":
        result = num1 * num2
        st.write(f"Result: {num1} × {num2} = {result}")
    elif operation == "Divide":
        if num2 != 0:
            result = num1 / num2
            st.write(f"Result: {num1} ÷ {num2} = {result}")
        else:
            st.write("Error: Division by zero is not allowed!")
