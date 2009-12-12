<p>Person: ${node.Person | h}</p>

<%

people = store.find(node.Person)

%>


<p>People: <br />

%for person in people:
  ${person.birthdate | h}<br />
%endfor

</p>

