import os
import yaml

from flask import Flask, render_template, url_for, flash, redirect, request, session
import pandas as pd

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)