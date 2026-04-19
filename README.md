# Quiz Bot Documentation

## Setup Guide
1. Clone the repository: `git clone https://github.com/officialshivampandey01-maker/quiz-bot.git`
2. Navigate to the project folder: `cd quiz-bot`
3. Install dependencies: `npm install`
4. Configure the bot by editing the `config.json` file.
5. Run the bot: `node index.js`

## Features List
- **User Interaction**: Provides a user-friendly interface for answering quiz questions.
- **Multiple Choice Questions**: Supports multiple choice quiz formats.
- **Leaderboards**: Keeps track of the scores of users.

## Commands
- `/start`: Initializes the quiz.
- `/help`: Provides help on how to use the bot.

## JSON Examples
### Configuration File
```json
{
  "token": "YOUR_BOT_TOKEN",
  "admin": "YOUR_DISCORD_ID"
}
```

### Sample Questions
```json
[
  {
    "question": "What is the capital of France?",
    "options": ["Paris", "London", "Berlin"],
    "answer": "Paris"
  }
]
```

## Troubleshooting
- **Bot not responding**: Ensure that your bot token is correct and that the bot is online.
- **Dependency issues**: Make sure all dependencies are installed correctly. Run `npm install` again if necessary.
