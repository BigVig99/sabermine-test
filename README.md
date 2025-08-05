
# Tasks API
# Setup

## Environment

First, create a new virtual envionment in the root directory (sabermine-test/) with 

```bash
python -m venv .venv 
``` 
and activate it using 
```bash
source .venv/bin/activate
```

Once complete install all dependencies 

```bash
pip install -r requirements.txt
```

## Database Setup 
To create the SQLite database and apply migrations run
```
alembic upgrade head
```

# Running 
## (Option 1) Run using uvicorn 
To run this locally without docker, simply run 
```
uvicorn app.main:app --reload
```

## (Option 2) Run using docker 
To run this using docker, we must first build the docker image with 

```
docker build -t task-api .
```

and then run the corresponding container using 

```
docker run -p 8000:8000 --name task-api task-api
```

Both of these result in the API being accessible at http://localhost:8000/

# Using the API
The following instructions detail API use. We assume that you've run the above setup, and with whichever choice you've made are now running  the API on http://localhost:8000/. Note that you can access the docs using http://localhost:8000/docs which provide information on how to use all of the endpoints

## Example 1: Creating a task
A task can be created by running 
```bash
curl -X 'POST' \
  'http://localhost:8000/tasks/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
           "title": "Example",
           "description": "Example Task",
           "priority": 1,
           "due_date": "2000-01-30T15:00:00"
       }'
```
Where **all** fields are compulsory. Failure to provide any field will return a **422** response.   
Furthermore, the individual fields must be of the following types  
```bash
{
  "title": string,
  "description":  string,
  "priority": int ,
  "due_date": datetime string
}
```

and failure to do so will also return a **422** response. 

If successful, the endpoint will return **200** response, with a JSON representation of the task you just created. In this case: 

```bash 
{
  "title":"Example",
  "description":"Example Task",
  "priority":1,
  "due_date":"2000-01-30T15:00:00",
  "id":1,
  "completed":false
}
```


## Example 2: Getting all tasks
### Pagination
All tasks can be retrieved and filtered using this endpoint.   
In the case where you want to retrieve all of the tasks without filtering, you start by calling with page number 1
```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/?page=1' \
  -H 'accept: application/json'
```
which will return a **200** response with a body of form
```bash 
{
  "total": 13,
  "next_url": "/tasks/?page=2",
  "prev_url": null,
  "items": [
    {
      "title": "Edited",
      "description": "Edited task",
      "priority": 2,
      "due_date": "2000-02-20T15:00:00",
      "id": 1,
      "completed": true
    },
    ...
    ]
}
```

Here, ```total``` gives you the full number of tasks, ```next_url``` the url for the next page, callable as before, ```prev_url``` will give you the URL to the previous page and ```items``` a list containing 5 tasks.  
 In the case we call the next page using 

```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/?page=2' \
  -H 'accept: application/json'
```

we recieve a similar response 

```bash 
{
  "total": 13,
  "next_url": "/tasks/?page=3",
  "prev_url": "/tasks/?page=1",
  "items": [
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 2,
      "due_date": "2000-01-30T15:00:00",
      "id": 6,
      "completed": false
    },
    ...
    ]
}    
```

But this time with a non null ```prev_url```   
Finally with 13 total tasks, a call for page 3 
```bash 
curl -X 'GET' \
  'http://localhost:8000/tasks/?page=3' \
  -H 'accept: application/json'
```

gives us 

```bash
{
  "total": 13,
  "next_url": null,
  "prev_url": "/tasks/?page=2",
  "items": [
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 3,
      "due_date": "2000-01-30T15:00:00",
      "id": 11,
      "completed": false
    },
    ...
    ]
}
```

where ```next_url``` is now null, allowing us to iterate over all tasks (infinite scrolling)

### Filtering 
Aside from page number, a set of query parameters can be supplied to the function to filter based on **completion status**, **priority** and also an **search string** which matches (infix) titles and descriptions. Note that this string is not case sensitive.

#### Example: Completion 
We can filter for completed tasks using 
```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/?completed=true&page=1' \
  -H 'accept: application/json'
```
to retrieve 

```bash
{
  "total": 1,
  "next_url": null,
  "prev_url": null,
  "items": [
    {
      "title": "Edited",
      "description": "Edited task",
      "priority": 2,
      "due_date": "2000-02-20T15:00:00",
      "id": 1,
      "completed": true
    }
  ]
}
```

Note that the existence of only 1 complete task (signified by a ```total``` of 1) means there's no next page here. 

#### Example: Priority 
Filtering for prioirty is extremely similar to completion, with a call like 
```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/?priority=1&page=1' \
  -H 'accept: application/json'
```
returning a **200** response with body

```bash
{
  "total": 3,
  "next_url": null,
  "prev_url": null,
  "items": [
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 2,
      "completed": false
    },
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 3,
      "completed": false
    },
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 4,
      "completed": false
    }
  ]
}
```
#### Example: Search 
We have the ability to search for strings in the description or the title, with a call like 

```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/?search_string=examp&page=1' \
  -H 'accept: application/json'
```

returning 

```bash 
{
  "total": 12,
  "next_url": "/tasks/?page=2",
  "prev_url": null,
  "items": [
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 2,
      "completed": false
    },
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 3,
      "completed": false
    },
```

#### Composite Filtering 
Finally, we can also apply all of these filtering criteria in a request like 
```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/?completed=false&priority=1&search_string=examp&page=1' \
  -H 'accept: application/json'
```
which in this case returns 

```bash
{
  "total": 3,
  "next_url": null,
  "prev_url": null,
  "items": [
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 2,
      "completed": false
    },
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 3,
      "completed": false
    },
    {
      "title": "Example",
      "description": "Example Task",
      "priority": 1,
      "due_date": "2000-01-30T15:00:00",
      "id": 4,
      "completed": false
    }
  ]
}
```
### Other 
The use of a non boolean completed flag,  non integer page number or priority, or an integer prioirty outside of {1,2,3} will all result in a **422** response with a body detailing the issue
## Example 3: Retrieve a specific task by ID 

Given a task ID <id>, you can retrieve the specific task by running 

```bash
curl -X 'GET' \
  'http://localhost:8000/tasks/<id>/' \
  -H 'accept: application/json'
```
In the case you enter an invalid ID (of a task that hasn't been created, or one that's been deleted), the endpoint will return a **404** response with body
```bash
{"detail":"Task not found."}
```
Should you enter an ID that is invalid because it cannot be parsed to an integer, say 's', you will recieve a **422** response.

Otherwise, you will recieve a **200** response with the task details 

```bash
{
  "title": "Example",
  "description": "Example Task",
  "priority": 1,
  "due_date": "2000-01-30T15:00:00",
  "id": 1,
  "completed": false
}
```
## Example 4: Updating an existing task 
An existing task with id <id> can be updated using a PUT request as follows: 

```bash
curl -X 'PUT' \
  'http://localhost:8000/tasks/<id>/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Edited",
  "description": "Edited task",
  "priority": 2,
  "due_date": "2000-02-20T15:00:00",
  "completed": true
}'
```
The payload itself takes the form 
```bash
{
  "title": string,
  "description": string,
  "priority": int,
  "due_date": datetime string,
  "completed": bool
}
```
where **all** fields are optional. 
As usual, calling with the id of a non-existent/deleted task will result in a **404** response with body 
```bash
{
  "detail": "Task not found."
}
```
and using a malformed/ non integer ID will give a **422**. 

A successful call will return a 200 response with body 

```bash
{
  "title": "Edited",
  "description": "Edited task",
  "priority": 2,
  "due_date": "2000-02-20T15:00:00",
  "id": 1,
  "completed": true
}
```
reflecting the new state of the task
## Example 5: Delete an existing task
To delete an existing task, say with task ID <id>, you can run 

```bash
curl -X 'DELETE' \
  'http://localhost:8000/tasks/<id>/' \
  -H 'accept: application/json'
```
If an integer ID corresponding to a non (or no longer) existing task is entered you will recieve a **404** response with body 
```
{
  "detail": "Task not found."
}
``` 
If a non integer ID is entered, you'll recieve a **422** as with the other endpoints  
A successful deletion will return a **200** response with body 

```bash 
{
  "message": "Task deleted successfully."
}
```

# Running tests 

Once setup is complete, you can run tests simply by running  
```
pytest
```
in root 


# Notes 
The repo is configured to run black to ensure PEP8 styling, and pytest to ensure the tests pass, where failure to verify each of these will cause the pipeline to fail. To check these locally, you can run 

```bash
black . 
```
To reformat code to conform to proper styling 
and 
```bash
pytest
```
to ensure all tests pass.

