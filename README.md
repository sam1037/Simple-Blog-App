# Simple Blog App

## Overview
Check it out [here](https://simple-blog-app-production.up.railway.app/)! (You can view as guest or create an account).

This is a Flask-based web application that implements a simple blog system with the following features:

- User authentication (login/logout and registration)
- Create, read, update, and delete blog posts as logged-in user (CRUD operations)
- Guest mode: read blogs without logging in as guest
- PostgreSQL database for data storage

## Tech Stack
- Frontend: HTML/JS/CSS, Tailwind CSS
- Backend: Python, Flask
- Database: PostgreSQL (hosted on Neon cloud platform)
- Testing: pytest
- Package Management: uv
- Tools: GitHub Actions, Railway, Neon, Ruff

## Commands
- `uv sync`: download the required packages
- `uv run flask --app src.app run`: run the Flask app
- `uv run -m pytest`: run the tests