# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

-   [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

-   [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

-   [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

## Database Setup

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle GET requests for all available categories.
4. Create an endpoint to DELETE question using a question ID.
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.
6. Create a POST endpoint to get questions based on category.
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422 and 500.

## API Reference

---

### Getting started

-   **Base URL**: At present, this application can only be run locally and is not hosted at a base URL. The backend application is hosted at the default `http://127.0.0.1:5000/`, which is set as a proxy in the front-end configuration.

-   **Authentication**: This version of the application does not require authentication or API keys.

### Error Handling

Errors are returned as JSON objects in the following format:

```sh
{
    "success": False,
    "error": 404,
    "message": "bad request"
}
```

The API will return four error types when requests fail:

-   400: Bad Request
-   404: Resource Not Found
-   405: Method Not Allowed
-   422: Not Processable
-   500: Internal Server Error

### Endpoints

##### GET /questions

---

-   **General**: Returns an object containing a list of questions, the number of total questions, all categories, and the current category. Results are paginated in groups of 10.

-   **Request Parameters**:

    -   **page number** (_optional_): Include a request argument to choose the page number, starting from 1

-   **Returns**: An object with the following attributes:

    -   **questions** (_object_): the trivia questions

    -   **total_questions** (_integer_): the number of total questions

    -   **current_category** (_string_): the current category

    -   **categories** _(object_): all available categories

-   **Sample Request**:

```sh
curl http://127.0.0.1:5000/questions
```

-   **Sample Response**:

```sh
{
    "questions": [
        {
            "id": 21,
            "question": "Who discovered penicillin?",
            "answer": "Alexander Fleming",
            "difficulty": 3,
            "category": "Science"
        }
    ],
    "total_questions": 19,
    "current_category": "Science",
    "categories": {
        1: "Science",
        2: "Art",
        3: "Geography",
        4: "History",
        5: "Entertainment",
        6: "Sports"
    }
}
```

##### POST /questions

---

-   **General**: Create a new question using the submitted question, answer, category, and difficulty rating.

-   **Request Parameters**:

    -   **question** (_string_): the question you want to add

    -   **answer** (_string_): the answer to the question you are adding

    -   **category** (_integer_): the id of the category the question belongs to

    -   **difficulty** (_integer_): the difficulty rating of the question; 1 being the easiest and 5 being the hardest

-   **Returns**: An object with the following attributes:

    -   **success** (_boolean_): the success value of the request

    -   **created_id** (_boolean_): the id of the newly created question

    -   **questions** (_objects_): the questions; paginated based on the current page number to update the front end

    -   **total_questions** (_integer_): the total number of questions; updated to reflect the newly created question

    -   **current_category** (_string_): the current category

    -   **categories** _(object_): all available categories

*   **Sample Request**:

```sh
curl http://127.0.0.1:5000/questions?page=3 -X POST -H "Content-Type: application/json" -d '{"question":"What is the largest lake in the United States?", "answer":"Lake Superior", "category":3, "difficulty":2}'
```

-   **Sample Response**:

```sh
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "created_id": 31,
  "current_category": null,
  "questions": [
    {
      "answer": "Louis Armstrong",
      "category": 5,
      "difficulty": 2,
      "id": 27,
      "question": "\"What a Wonderful World\" is a jazz song first recorded by which American singer?"
    },
    {
      "answer": "Lake Superior",
      "category": 3,
      "difficulty": 2,
      "id": 31,
      "question": "What is the largest lake in the United States?"
    }
  ],
  "success": true,
  "total_questions": 22
}
```

##### DELETE /questions/{question_id}

---

-   **General**: Returns an object containing a success value, the id of the deleted question, list of questions based on the current page (to update the frontend), the number of total questions (updated to reflect the deleted question), all categories, and the current category. Results are paginated in groups of 10.

-   **Request Parameters**:

    -   **question_id**: the id of the question you'd like to delete

-   **Returns**: An object with the following attributes:

    -   **success** (_boolean_): the success value

    -   **deleted_id** (_integer_): the id of the deleted question

    -   **questions** (_object_): the trivia questions

    -   **total_questions** (_integer_): the number of total questions

    -   **current_category** (_string_): the current category

    -   **categories** _(object_): all available categories

-   **Sample Request**:

```sh
curl -X DELETE http://127.0.0.1:5000/questions/30
```

-   **Sample Response**:

```sh
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null,
  "deleted_id": 30,
  "questions": [
    {
      "answer": "Louis Armstrong",
      "category": 5,
      "difficulty": 2,
      "id": 27,
      "question": "\"What a Wonderful World\" is a jazz song first recorded by which American singer?"
    }
  ],
  "success": true,
  "total_questions": 21
}
```

##### POST /questions-search

---

-   **General**: Get questions based on a given search term. Returns any questions for whom the search term is a substring of the question.Results are paginated in groups of 10.

-   **Request Parameters**:

    -   **searchTerm** (_string_): the search term used to look for questions

-   **Returns**: An object with the following attributes:

    -   **questions** (_objects_): all questions that include the searchTerm string within the question

    -   **total_questions** (_integer_): the total number of questions that match the search term

    -   **current_category** (_string_): the current category

    -   **categories** _(object_): all available categories

*   **Sample Request**:

```sh
curl http://127.0.0.1:5000/questions-search -X POST -H "Content-Type: application/json" -d '{"searchTerm":"title"}'
```

-   **Sample Response**:

```sh
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null,
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "total_questions": 2
}
```

##### GET /categories

---

-   **General**: Returns an object containing containing a single key, "categories." The value is an object in which each key is a category id and each value is the corresponding category name.

-   **Request Parameters**:

    -   **none**

-   **Returns**: An object with the following attributes:

    -   **categories** _(object_): all available categories

-   **Sample Request**:

```sh
curl http://127.0.0.1:5000/categories
```

-   **Sample Response**:

```sh
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

##### GET /categories/{category_id}/questions

---

-   **General**: Returns an object containing a list of questions belonging to the given categorye, the number of total questions across all categories, the current category, and all categories. Results are paginated in groups of 10.

-   **Request Parameters**:

    -   **category_id** (_integer_): the id of the chosen category

-   **Returns**: An object with the following attributes:

    -   **questions** (_object_): the trivia questions that fall under the given category

    -   **total_questions** (_integer_): the total number of questions that match the category

    -   **current_category** (_string_): the current category

    -   **categories** _(object_): all available categories

-   **Sample Request**:

```sh
curl -X GET http://127.0.0.1:5000/categories/1/questions
```

-   **Sample Response**:

```sh
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": 1,
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    },
    {
      "answer": "Blood",
      "category": 1,
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ],
  "total_questions": 22
}
```

##### POST /quizzes

---

-   **General**: Takes category and previous question parameters and returns a random question (that has not been previously answered) within the given category (if provided).

-   **Request Parameters**:

    -   **previous_questions** (_list_): the ids (_integers_) of questions that were previously answered

    -   **quiz_category** (_object_): an object whith a single key, id (_string_) and a single value, the id (_integer_) of the chosen category; use zero to include all categories

-   **Returns**: An object with the following attributes:

    -   **question** (_string_): the next question to be used in the quiz; will return **False** (_boolean_), if there are no more questions left to answer

*   **Sample Request**:

```sh
curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions":[20, 22], "quiz_category":{"id":1}}'
```

-   **Sample Response**:

```sh
{
  "question": {
    "answer": "Alexander Fleming",
    "category": 1,
    "difficulty": 3,
    "id": 21,
    "question": "Who discovered penicillin?"
  }
}
```

## Testing

To run the tests, run

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
