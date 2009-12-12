<p>People: <br />

%for person in people:
  ${person.name | h}: ${person.birthdate | h}<br />
%endfor

</p>

