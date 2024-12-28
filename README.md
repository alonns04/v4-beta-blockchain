# Proyecto de Firmas Asimétricas para Analíticos Universitarios y Tecnología Blockchain
   
## Descripción

El sistema permite generar y verificar analíticos y certificados de analiticos universitarios de forma segura. Utiliza claves públicas y privadas para firmar electrónicamente los documentos, asegurando que solo el emisor autorizado (la institución para el analítico y el estudiante para el certificado) pueda validarlos. 
Este proyecto implementa un sistema de verificación de diplomas y analíticos universitarios utilizando firmas asimétricas y el algoritmo SHA3-256, integrado en una blockchain. La blockchain se utiliza para asegurar la integridad y autenticidad de los documentos generados.


## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
2. Crear un entorno virtual:
   ```bash
    python3 -m venv venv
    source venv/bin/activate  # Para Linux/Mac
    venv\Scripts\activate     # Para Windows
3. Instalar las dependencias:
   ```bash
    pip install -r requirements.txt
4. Ejecutar la aplicación:
   ```bash
    python app.py


### Funcionalidades

- **Generación de claves**: Los usuarios (instituciones y estudiantes) pueden generar sus propias claves públicas y privadas.
- **Generación de analíticos**: Los analíticos de los estudiantes se generan automáticamente con la opción de incluir cursos y otras informaciones académicas.
- **Blockchain**: Los diplomas y analíticos se almacenan en una blockchain para garantizar su integridad e inmutabilidad.
- **Verificación de firmas**: Los usuarios pueden verificar las firmas digitales de los estudiantes y las instituciones mediante el uso de las claves públicas.
  
## Tecnologías Utilizadas

- **Python**: El lenguaje principal para el backend.
- **Flask**: Framework para la creación de aplicaciones web.
- **Flask-SocketIO**: Para la comunicación en tiempo real mediante WebSockets.
- **PyCryptodome**: Biblioteca para criptografía, que incluye la implementación de algoritmos de firma (PS) y SHA3-256.
- **Blockchain**: Implementación propia de la blockchain para almacenar los registros académicos de los estudiantes de manera segura.


## Uso
### Generar claves
Se puede generar un par de claves públicas y privadas utilizando el endpoint /generate_keys o a través de la interfaz web del proyecto.

### Crear y ver un analítico
Los estudiantes pueden llenar un formulario con su nombre, DNI, institución, cursos y fecha de emisión. El sistema generará un hash SHA3-256 del analítico, y el documento se firmará electrónicamente con las claves privadas.

### Verificar la firma
La firma digital de los documentos se puede verificar utilizando el endpoint /verify_signature. La firma se valida usando la clave pública correspondiente.

### Ver el estado de la Blockchain
La blockchain puede visualizarse en tiempo real a través del endpoint /blockchain, que proporciona información sobre los bloques y sus firmas.
