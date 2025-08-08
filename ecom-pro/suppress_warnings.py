import warnings
import os

# Supprimer les warnings de dépréciation
warnings.filterwarnings("ignore", category=UserWarning, module="rest_framework_simplejwt")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Variable d'environnement pour Node.js
os.environ['NODE_NO_WARNINGS'] = '1'