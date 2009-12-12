<%inherit file="/site.mak"/>

<p>Hello, this is a demo page with a login box.</p>

<p>Avatar: ${request.avatar | h}</p>

% if request.avatar:
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