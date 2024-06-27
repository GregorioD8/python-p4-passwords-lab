#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class Signup(Resource):
    
    def post(self):
        # Get the username and password from the request JSON
        username = request.get_json()['username']
        password = request.get_json()['password']
        
        # Check if both username and password are provided
        if username and password:
            # Create a new User instance
            new_user = User(username=username)
            # Set the password hash for the new user
            new_user.password_hash = password
            # Add the new user to the database session
            db.session.add(new_user)
            db.session.commit()

            # Set the 'user_id' in the session to the new user's ID
            session['user_id'] = new_user.id
            # Return the new user data as JSON with status code 201 Created
            return new_user.to_dict(), 201

        return {'error': '422 Unprocessable Entity'}, 422
    

class CheckSession(Resource):
    def get(self):
        
        # Check if 'user_id' is in the session
        if session.get('user_id'): 
            # Query the user by ID
            user = User.query.filter(User.id == session['user_id']).first()
            # Return the user data as JSON with status code 200 OK
            return user.to_dict(), 200
        # Return an empty response with status code 204 No Content if not logged in
        return {}, 204 

class Login(Resource):
    
    def post(self):
        
        # Get the username from the request JSON
        username = request.get_json()['username']
        # Get the password from the request JSON
        password = request.get_json()['password']

        # Query the user by username
        user = User.query.filter(User.username == username).first()

         # Check if the user exists and the password is correct
        if user.authenticate(password):
            # Set the 'user_id' in the session to the user's ID
            session['user_id'] = user.id
            # Return the user data as JSON with status code 200 OK
            return user.to_dict(), 200
        
        # Return an error if authentication fails
        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):

        # Clear the 'user_id' in the session
        session['user_id'] = None
        # Return an empty response with status code 204 No Content
        return {}, 204
    
# Add resources to the API with their respective endpoints
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
