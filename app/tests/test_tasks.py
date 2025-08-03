from app.utils.constants import TASKS_PAGE_SIZE


def test_tasks_can_be_fetched_without_filtering(client, task_factory):
    task_titles = {f"Test task {i}" for i in range(6)}

    for title in task_titles:
        task_factory(title=title)

    retrieved_tasks = []

    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 6
    assert data['prev_url'] is None
    results = data['items']
    assert len(results) == TASKS_PAGE_SIZE
    retrieved_tasks.extend(results)
    next_page = data['next_url']

    response = client.get(next_page)
    data = response.json()

    assert data['prev_url'] is not None
    results = data['items']
    assert len(results) == 1
    retrieved_tasks.extend(results)

    assert set([task['title'] for task in retrieved_tasks]) == task_titles


