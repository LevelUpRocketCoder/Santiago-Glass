Set WshShell = CreateObject("WScript.Shell")
' Lanzar el servidor de Django de forma oculta
WshShell.Run "cmd.exe /c """"C:\Users\My PC\OneDrive\Desktop\santi\santiago_glass\venv\Scripts\python.exe"" ""C:\Users\My PC\OneDrive\Desktop\santi\santiago_glass\manage.py"" runserver 127.0.0.1:8000""", 0, False
' Esperar 3 segundos para asegurar que el servidor arrancó
WScript.Sleep 3000
' Abrir el navegador por defecto
WshShell.Run "http://127.0.0.1:8000"
