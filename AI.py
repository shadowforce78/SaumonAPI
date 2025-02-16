from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI")

datajson = """
    [
  {
    "federationId": null,
    "entityType": 0,
    "elements": [
      {
        "label": "Heure",
        "content": "20/02/2025 08:00-09:00",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Matière",
        "content": "IN2R01",
        "federationId": "IN2R01",
        "entityType": 100,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Personnel",
        "content": "OSTER Alain",
        "federationId": "60093",
        "entityType": 101,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Groupe",
        "content": "INF1-B",
        "federationId": "INF1-B",
        "entityType": 103,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Salle",
        "content": "315 - VEL",
        "federationId": "315 - VEL",
        "entityType": 102,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Catégorie d’événement",
        "content": "Travaux Dirigés (TD)",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Remarques",
        "content": null,
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": true,
        "isStudentSpecific": false
      }
    ]
  },
  {
    "federationId": null,
    "entityType": 0,
    "elements": [
      {
        "label": "Heure",
        "content": "20/02/2025 09:00-11:00",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Matière",
        "content": "IN2R01",
        "federationId": "IN2R01",
        "entityType": 100,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Personnel",
        "content": "OSTER Alain",
        "federationId": "60093",
        "entityType": 101,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Groupe",
        "content": "INF1-B",
        "federationId": "INF1-B",
        "entityType": 103,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Salle",
        "content": "G25 - VEL",
        "federationId": "G25 - VEL",
        "entityType": 102,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Catégorie d’événement",
        "content": "Travaux Dirigés (TD)",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Remarques",
        "content": null,
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": true,
        "isStudentSpecific": false
      }
    ]
  },
  {
    "federationId": null,
    "entityType": 0,
    "elements": [
      {
        "label": "Heure",
        "content": "20/02/2025 13:00-16:00",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Matières",
        "content": "IN2R08",
        "federationId": "IN2R08",
        "entityType": 100,
        "assignmentContext": "a-start",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": null,
        "content": "IN2R12",
        "federationId": "IN2R12",
        "entityType": 100,
        "assignmentContext": "a-end-0",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Personnel",
        "content": "CUKALLA Etleva",
        "federationId": "19781",
        "entityType": 101,
        "assignmentContext": "a-start",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": null,
        "content": "OSTER Alain",
        "federationId": "60093",
        "entityType": 101,
        "assignmentContext": "a-end-0",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Groupe",
        "content": "INF1-B",
        "federationId": "INF1-B",
        "entityType": 103,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Salle",
        "content": "314 - VEL",
        "federationId": "314 - VEL",
        "entityType": 102,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Catégorie d’événement",
        "content": "Travaux Pratiques (TP)",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Remarques",
        "content": null,
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": true,
        "isStudentSpecific": false
      }
    ]
  },
  {
    "federationId": null,
    "entityType": 0,
    "elements": [
      {
        "label": "Heure",
        "content": "20/02/2025 16:00-17:00",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Matière",
        "content": "IN2R12",
        "federationId": "IN2R12",
        "entityType": 100,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Personnel",
        "content": "CUKALLA Etleva",
        "federationId": "19781",
        "entityType": 101,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Groupe",
        "content": "INF1-B",
        "federationId": "INF1-B",
        "entityType": 103,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Salle",
        "content": "414 - VEL",
        "federationId": "414 - VEL",
        "entityType": 102,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Catégorie d’événement",
        "content": "Travaux Dirigés (TD)",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Remarques",
        "content": null,
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": true,
        "isStudentSpecific": false
      }
    ]
  },
  {
    "federationId": null,
    "entityType": 0,
    "elements": [
      {
        "label": "Heure",
        "content": "20/02/2025 11:00-12:00",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Matière",
        "content": "IN2R01",
        "federationId": "IN2R01",
        "entityType": 100,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Personnel",
        "content": "ROBBA Isabelle",
        "federationId": "517",
        "entityType": 101,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Groupe",
        "content": "INF1",
        "federationId": "INF1",
        "entityType": 103,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Salle",
        "content": "Amphi B - VEL",
        "federationId": "Amphi B - VEL",
        "entityType": 102,
        "assignmentContext": "a-start-end",
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Catégorie d’événement",
        "content": "Contrôles Continus (CC)",
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": false,
        "isStudentSpecific": false
      },
      {
        "label": "Remarques",
        "content": null,
        "federationId": null,
        "entityType": 0,
        "assignmentContext": null,
        "containsHyperlinks": false,
        "isNotes": true,
        "isStudentSpecific": false
      }
    ]
  }
]
"""
prompt = (
    "Reorganise les données suivantes en un tableau lisible :"
    + datajson
    + " , je ne veux que du json brut"
)

client = genai.Client(api_key=gemini_api_key)

response = client.models.generate_content_stream(
    model="gemini-2.0-flash",
    contents=[prompt],
)

for chunk in response:
    # Remove any markdown formatting and print raw text
    cleaned_text = chunk.text.replace("```", "").replace("```", "").strip()
    if cleaned_text:  # Only print if there's content after cleaning
        print(cleaned_text, end="")
