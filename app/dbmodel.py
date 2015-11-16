from mongoengine import *
import json
from flask import Flask, abort, request, jsonify, g, url_for
from app import app, conn
import cPickle
from app.auth import User

class Project(Document):
    name = StringField(unique=True)
    user = ReferenceField(User)
    windHeight = IntField()
    windTMatrix = BinaryField()
    windSeasonality = BinaryField()
    
    def save_TMatrix(self,tmat):
        #convert transition matrix to binary and assign
        self.windTMatrix = cPickle.dumps(tmat, protocol=2)
    
    def get_TMatrix(self):
        if self.windTMatrix:
            return cPickle.loads(self.windTMatrix)
        else: return None

    def save_Seasonality(self,matrix):
        #convert transition matrix to binary and assign
        self.windSeasonality = cPickle.dumps(matrix, protocol=2)
    
    def get_Seasonality(self):
        if self.windSeasonality:
            return cPickle.loads(self.windSeasonality)
        else: return None
        
    def save_Stationary(self,matrix):
        #convert transition matrix to binary and assign
        self.windStationary = cPickle.dumps(matrix, protocol=2)
    
    def get_Stationary(self):
        if self.windStationary:
            return cPickle.loads(self.windStationary)
        else: return None
    
    
        
        
        
        
        
        
    
    
    
