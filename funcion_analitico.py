import os
import json


def create_transcript(student_name, student_dni, institution_name, courses, issue_date):
    # Formatear el DNI para que tenga 20 dígitos
    formatted_dni = str(student_dni).zfill(20)
    
    # Calcular el promedio de las notas
    total_notas = sum(course['nota'] for course in courses.values())
    cantidad_materias = len(courses)
    promedio = float(total_notas / cantidad_materias) if cantidad_materias > 0 else 0
    promedio = round(promedio, 2)
    
    transcript = {
        "name": student_name,
        "dni": formatted_dni,
        "institution": institution_name,
        "courses": courses,
        "average": promedio,
        "issue_date": issue_date
    }
    return transcript

