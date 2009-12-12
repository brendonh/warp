<%inherit file="/site.mak"/>

<p>Hello, this is a demo page with a login box.</p>

<p>Avatar: <strong>${request.avatar | h}</strong></p>

% if request.avatar:
<form method="POST" action="/__logout__/demo/">
<input type="submit" value = "Log Out" />
</form>
% else:
<form method="POST" action="/__login__/demo/">
  Email: <input type="text" name="email" /><br />
  Pass: <input type="text" name="password" /><br />
  <input type="submit" value="Log in" />
</form>
% endif