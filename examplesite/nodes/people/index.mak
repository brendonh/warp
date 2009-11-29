<p>Hello, this is the people page.</p>

<p>Person: ${node.Person | h}</p>

<p>Avatar: ${avatar | h}</p>

% if avatar:
<form method="POST" action="/__logout__">
<input type="submit" value = "Log Out" />
</form>
% else:
<form method="POST" action="/__login__">
  Email: <input type="text" name="email" /><br />
  Pass: <input type="text" name="password" /><br />
  <input type="submit" value="Log in" />
</form>
% endif