import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.subject import Subject
from app.models.topic import Topic
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.session import Session as QuizSession
from app.common.enums import QuestionType, DeliveryMode, VisibilityType, DifficultyLevel


def test_teacher_submissions_grading_endpoints(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    student_headers: dict,
    test_teacher,
    test_student,
):
    # 1. Create parent Subject & Topic
    subject = Subject(name="Distributed Systems", code="CS05")
    db.add(subject)
    db.commit()

    topic = Topic(subject_id=subject.id, name="Consensus", code="CONS01")
    db.add(topic)
    db.commit()

    # 2. Create question
    question = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Explain Paxos consensus.",
        question_type=QuestionType.TEXT,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.HARD,
        default_marks=Decimal("30.00"),
        default_time_limit_seconds=600,
    )
    db.add(question)
    db.commit()

    # 3. Create Quiz
    quiz = Quiz(title="Paxos Consensus Assignment", created_by=test_teacher.id, is_active=True)
    db.add(quiz)
    db.commit()

    qq = QuizQuestion(quiz_id=quiz.id, question_id=question.id, question_order=1, marks=Decimal("30.00"))
    db.add(qq)
    db.commit()

    # 4. Create Session in ASSIGNMENT mode
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="PAXOS",
        delivery_mode=DeliveryMode.ASSIGNMENT,
    )
    db.add(session)
    db.commit()

    # 5. Student Joins the session
    join_payload = {"room_code": "PAXOS"}
    response = client.post("/api/v1/participants/join", json=join_payload, headers=student_headers)
    assert response.status_code == 201
    part_id = response.json()["data"]["id"]

    # 6. Student submits TEXT assignment response
    answer_payload = {
        "question_id": str(question.id),
        "selected_answer": {"text": "Paxos is a family of protocols for solving consensus..."},
        "response_time_ms": 25000,
        "submission_status": "SUBMITTED"
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 201
    submission_id = response.json()["data"]["id"]

    # 7. Teacher views all submissions for the quiz
    response = client.get(f"/api/v1/quizzes/{quiz.id}/submissions", headers=teacher_headers)
    assert response.status_code == 200
    submissions = response.json()["data"]
    assert len(submissions) >= 1
    assert submissions[0]["id"] == submission_id

    # 8. Teacher views submissions filtering by status SUBMITTED
    response = client.get(f"/api/v1/quizzes/{quiz.id}/submissions?status=SUBMITTED", headers=teacher_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1

    # 9. Teacher views submissions filtering by status DRAFT (should return empty list)
    response = client.get(f"/api/v1/quizzes/{quiz.id}/submissions?status=DRAFT", headers=teacher_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 0

    # 10. Teacher views submissions searching by student name
    response = client.get(f"/api/v1/quizzes/{quiz.id}/submissions?search=student", headers=teacher_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1

    # 11. Teacher views single submission details
    response = client.get(f"/api/v1/quizzes/{quiz.id}/submissions/{submission_id}", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == submission_id

    # 12. Teacher grades the submission via POST endpoint
    grade_payload = {
        "score_awarded": 27.50,
        "feedback": "Outstanding details about Paxos phases.",
        "is_correct": True
    }
    response = client.post(
        f"/api/v1/quizzes/{quiz.id}/submissions/{submission_id}/grade",
        json=grade_payload,
        headers=teacher_headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["grading_status"] == "GRADED"
    assert response.json()["data"]["submission_status"] == "GRADED"
    assert float(response.json()["data"]["score_awarded"]) == 27.50
    assert response.json()["data"]["feedback"] == "Outstanding details about Paxos phases."
