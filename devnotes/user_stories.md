# User Stories for **PyByteSize**

1. **As a developer dealing with large file uploads**,  
   I want to quickly convert raw byte counts into a human-friendly format (e.g., `MB`, `GB`, `MiB`, `GiB`),  
   so that I can present file sizes in a readable manner to my users.

2. **As a systems administrator**,  
   I want to perform block-aligned calculations (e.g., calculating actual on-disk usage),  
   so that I can precisely track and allocate storage resources.

3. **As a data engineer**,  
   I want to subtract, add, and compare file sizes without manually juggling unit multipliers,  
   so that my data processing pipelines remain clean and consistent.

4. **As a backend developer working on cloud storage integrations**,  
   I want to take a raw byte size from an API response and easily convert and format it for logs,  
   so that I can maintain standardized monitoring reports across multiple services.

5. **As a CLI tool author**,  
   I want to provide users a command-line interface that accepts human-readable sizes like `10MB`,  
   so that they can specify memory and storage limits without converting those values manually.

6. **As a performance analyst**,  
   I want to calculate throughput by dividing transferred bytes by time in seconds,  
   so that I can obtain a new `PyByteSize` object to display with either metric or binary prefixes.

7. **As a Python library maintainer**,  
   I want a fully tested, type-annotated module for sizes,  
   so that my project’s dependencies remain stable and easy to maintain.

8. **As an application developer building file management utilities**,  
   I want to display file sizes in either metric or binary prefixes (e.g., `MB` vs. `MiB`) depending on user preference,  
   so that my application meets the needs of different audiences (tech-savvy vs. casual end users).
