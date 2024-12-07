from flask import Blueprint, redirect, url_for, render_template, request, send_file, jsonify
import os
from .extentions import db
from .models import Devices, MetadataValues, Firmware
from google.cloud import storage
import io
import json
from google.oauth2 import service_account
from dotenv import load_dotenv
from intelhex import IntelHex
from datetime import datetime

load_dotenv()

propertymngt = Blueprint('propertymngt', __name__)

@propertymngt.route('/')
def index():
    print('Device storage is full!')
    return {'message': 'Device storage is full!'}