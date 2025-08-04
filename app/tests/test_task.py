from datetime import timedelta, datetime


def test_request_for_non_existent_task_returns_404(
    client,
    task_factory,
):
    placeholder_task = task_factory()
    res = client.put(f"/tasks/{placeholder_task.id + 1}/", json={})
    assert res.status_code == 404
    assert res.json()["detail"] == "Task not found."


def test_request_for_modifying_task_with_empty_payload_returns_200_and_leaves_task_unmodified(
    client, task_factory
):
    task_to_edit = task_factory(
        title="To Edit",
        description="Task to edit",
        completed=False,
        priority=1,
        due_date=datetime.now() + timedelta(days=1),
    )
    res = client.put(f"/tasks/{task_to_edit.id}/", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == task_to_edit.title
    assert data["description"] == task_to_edit.description
    assert data["priority"] == task_to_edit.priority
    assert datetime.fromisoformat(data["due_date"]) == task_to_edit.due_date
    assert data["completed"] == task_to_edit.completed


def test_request_for_modifying_task_with_invalid_priority_returns_422_and_leaves_task_unmodified(
    client,
    task_factory,
    db_session,
):
    due_date = datetime.now() + timedelta(days=1)
    task_to_edit = task_factory(
        title="To Edit",
        description="Task to edit",
        completed=False,
        priority=1,
        due_date=due_date,
    )
    res = client.put(f"/tasks/{task_to_edit.id}/", json={"priority": 10})
    assert res.status_code == 422
    [details] = res.json()["detail"]
    assert details["msg"] == "Input should be 1, 2 or 3"

    db_session.refresh(task_to_edit)
    assert task_to_edit.priority == 1
    assert task_to_edit.title == "To Edit"
    assert task_to_edit.description == "Task to edit"
    assert task_to_edit.completed == False
    assert task_to_edit.due_date == due_date


def test_request_for_modifying_permitted_fields_of_task_returns_200_and_modifies_task_correctly(
    client,
    task_factory,
    db_session,
):
    task_to_edit = task_factory(
        title="To Edit",
        description="Task to edit",
        completed=False,
        priority=2,
        due_date=datetime.now() + timedelta(days=1),
    )
    edit_payload = {
        "title": "Edited Task",
    }
    res = client.put(f"/tasks/{task_to_edit.id}/", json=edit_payload)
    assert res.status_code == 200
    db_session.refresh(task_to_edit)
    assert task_to_edit.title == edit_payload["title"]
