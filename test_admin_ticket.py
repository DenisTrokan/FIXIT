from app import app, db, Ticket
from flask import session
import traceback

app.testing = True
with app.app_context():
    t = Ticket.query.first()
    if not t:
        print('No ticket found - creating a test ticket')
        t = Ticket(ticket_type='TECNICO', requester_name='Tester', description='Test ticket')
        db.session.add(t)
        db.session.commit()
    ticket_id = t.id
    print('Using ticket id', ticket_id)
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['is_superuser'] = True
        sess['username'] = 'admin'
    try:
        resp = client.get(f'/admin/ticket/{ticket_id}')
        print('STATUS', resp.status_code)
        data = resp.get_data(as_text=True)
        print('BODY_START')
        print(data[:4000])
        print('BODY_END')
    except Exception:
        traceback.print_exc()
