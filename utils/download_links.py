import base64

def generate_download_link(data, file_name, mime):
    """
    Generates an auto-download link for the given data.
    """
    if isinstance(data, str):
        data = data.encode()
    b64 = base64.b64encode(data).decode()
    html = f"""
    <html>
      <head>
        <script>
          window.onload = function() {{
            var a = document.createElement('a');
            a.href = "data:{mime};base64,{b64}";
            a.download = "{file_name}";
            document.body.appendChild(a);
            a.click();
          }};
        </script>
      </head>
      <body></body>
    </html>
    """
    return html
