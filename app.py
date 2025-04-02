import streamlit as st

# Add a title
st.title("Hello, world!")

# Start a new form
with st.form(key='my_form'):
    # Create a text input field
    user_input = st.text_input(label="Enter some text")

    # Create a submit button
    submitted = st.form_submit_button(label="Send")

# Display the user's input if the form was submitted
if submitted:
    st.write(f"You entered: {user_input}")
