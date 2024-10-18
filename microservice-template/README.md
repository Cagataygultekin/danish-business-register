# How to use this template
See below for the reason behind each component. 
```
microservice-template/
│
├── app/                         # Application code for the microservice.
│   ├── controller/              # Controllers to handle API requests
│   │   ├── init.py
│   │   └── example_controller.py 
│   │
│   ├── dtos/                    # Data Transfer Objects (DTOs)
│   │   ├── init.py
│   │   └── example.py           
│   │
│   ├── repositories/            # Data access layer (repositories)
│   │   └── init.py
│   │
│   ├── services/                # Business logic services
│   │   ├── init.py
│   │   ├── example_service.py   
│   │   ├── app_factory.py       # Application factory pattern setup
│   │   ├── config.py            # Configuration settings for the app, ALL environment variables of this project.
│   │   └── exceptions.py        # Custom exceptions for the services, caught in the controllers.
│
├── your_microservice/           # Your microservice-specific code
│   └── init.py
│
├── README.md                    # This documentation file
├── requirements.txt             # Python dependencies
└── run.py                       # Script to start the application
```

### Controllers

Controllers handle API requests and manage the flow of data between the service layer and the client. This is the entry point for requests into the system.

### DTOs

DTOs (Data Transfer Objects) represent simple data structures that are passed between layers. They ensure data is structured in a predictable way when interacting with the controllers, services, and repositories.

### Repositories

Repositories provide a layer of abstraction for data access logic. They interact with the database or any other data sources directly and provide the required data to the services.

### Services

Services contain the business logic of the application. They interact with the repositories and manage core operations, ensuring that the application’s logic is centralized in one place.

### Microservice Code

The `your_microservice/` directory allows you to separate any specific microservice code, keeping the core business logic and microservice-specific operations separate.

## Coding Conventions

1. **Docstring Standards:**
   - In every method or function's docstring, exceptions must be documented clearly.
   - Example format in docstring:
     ```python
     """
     :raises:
         CustomException: Description of why the exception is raised
     """
     ```

2. **Layered Architecture Flow:**
   - The flow of the application must follow a strict order:

     ```plaintext
     +------------------+
     |      Client      |
     +------------------+
               |
               v
     +------------------+
     |    Controller    |
     +------------------+
               |
               v
     +------------------+
     |     Services     |
     +------------------+
       /           |      \
      /            |       \
     +--------+  +--------+  +------------------+
     |  Repo  |  | Service|  | Your Microservice|
     +--------+  +--------+  +------------------+
    ```


3. **Exception Handling:**
   - All exceptions in the system are to be caught in the controllers. This ensures that the service and repository layers are free from handling errors directly. Instead, they should throw exceptions that are handled gracefully in the controllers.
   
     - Controllers should capture exceptions like this:
       ```python
       try:
           # Call service method
       except CustomException as e:
           return {"message": str(e)}, 400
       ```

   - Each service should raise meaningful exceptions, and they must be documented clearly in the docstrings of both the service and controller layers.

## Getting Started

### Prerequisites

To set up this project, you need Python 3.x and the dependencies listed in `requirements.txt`.

### Build a Docker Image for Google Cloud Run
```bash 
docker build --platform linux/amd64 -t [LOCATION]-docker.pkg.dev/[PROJECT_ID]/[ARTIFACT_REGISTRY_NAME]/v[MAJOR_VERSION].[SUB_VERSION].[SUBSUB_VERSION] .```