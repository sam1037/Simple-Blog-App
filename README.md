# Simple Blog App

## Overview
Check it out [here](https://simple-blog-app-production.up.railway.app/)!
(use username `test` and password `pw`).

This is a Flask-based web application that implements a simple blog system with the following features:

- User authentication (login/logout and registration)
- Create, read, update, and delete blog posts (CRUD operations)
- PostgreSQL database for data storage

## Tech Stack
- Frontend: HTML/JS/CSS, Tailwind CSS
- Backend: Python, Flask
- Database: PostgreSQL (hosted on Neon cloud platform)
- Testing: pytest
- Package Management: uv
- Tools: GitHub Actions, Railway (hosting), Neon

## Commands
- `uv sync`: download the required packages
- `uv run -m src.app`: run the Flask app
- `uv run -m pytest`: run the tests