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
  <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/socket.io.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>

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
</p>

<div id="messages">'''

EPILOGUE = '''
</div>
<div id="fuckWebDev"></div>
<script>
  if (location.port == 8080) {
    var namespace = '/socket.io/chat';
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    socket.on('message', function (msg) {
      $('#topic').html(msg.topic);
      $('#messages').append(msg.msg);
      $('html, body').animate({ scrollTop: $('#fuckWebDev').offset().top}, 1000);
    });
  }
</script>
</body></html>'''
