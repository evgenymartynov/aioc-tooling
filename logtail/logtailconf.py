COLOURS = [
  "#000000",
  "#000080",
  "#008000",
  "#FF0000",
  "#804040",
  "#8000FF",
  "#808000",
  "#008080",
  "#00FFFF",
  "#0000FF",
  "#FF00FF",
  "#808080",
  "#C0C0C0",
]

PROLOGUE = '''\
<html>
<head>
  <style>
    body {
        font-family: monospace, Monospace, 'Courier New';
        font-size: smaller;
    }

    .timestamp {
        color: #bbb;
    }

    .server {
        color: #a22;
    }

    .nick {
        color: #555;
    }

    .links-top * {
        color: #00c;
    }

    .topic-header {
        color: #000;
        font-weight: bold;
    }

    .topic {
        color: #44a;
    }
  </style>
</head>
<body>
<p class="links-top">
  [ <a href="aioc">small</a> | <a href="aioc-large">large</a> | Find/want something? <a href="https://github.com/evgenymartynov/aioc-tooling">Contribute</a> ]
</p>'''

EPILOGUE = '</body></html>'
