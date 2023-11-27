<samp>

# Sarufi Africa's Talking Voice Blueprint

This repository contains a FastAPI application for handling voice call requests, specifically designed for integration with Africa's Talking Voice API. The application utilizes the Sarufi library for natural language processing in voice interactions.

## Getting Started

### Prerequisites

1. **Python**: Make sure you have Python installed on your machine. You can download it from [python.org](https://www.python.org/).

2. **Dependencies**: Install the required dependencies by running the following command in the project's root directory:

```bash
pip install -r requirements.txt
```
### Environment Variables

Set up the necessary environment variables. Create a .env file in the root directory of the project and add the following:

```bash 
SARUFI_API_KEY=your_sarufi_api_key
SARUFI_BOT_ID=your_sarufi_bot_id
```

> Replace your_sarufi_api_key and your_sarufi_bot_id with your actual Sarufi API key and bot ID.

### Running the Application

To run the application, execute:

```bash
uvicorn main:app --reload
```

This will start the FastAPI server on the default port 8000.

### Usage

Once the server is running, it will be listening for POST requests at the /voicemail endpoint. 

1. sessionId
2. isActive
3. dtmfDigits

> Use Ngrok or Replit to deploy your webhook so that it can be available on the internet, ready to start receiving requests. 

### Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

### License

This project is licensed under the MIT License.

</samp>
