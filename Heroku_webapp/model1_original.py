{% extends 'base.html' %}

{% block head %}  {% endblock %}


{% block body %}
<h1> Email Contextualization Search Tool </h1>

<form action="/"  method="POST" >    
    
    
    <br>Include / Exclude following groups
      

      <div id="Enron_choices" style="display:True;">
        <ul class="checkbox-grid" > 
      
          <li><input type="checkbox"  name="choice11" value="lay-k" /> <label for="choice11">Lay-K</label> </li>
          <li><input type="checkbox"  name="choice11" value="skilling-j"/> <label for="choice13">Skilling-J</label></li>
          <li><input type="checkbox"  name="choice11" value="all"/> <label for="choice15">All</label></li>
          
        </ul>
      </div>
      
    
    <h4>Enter your query here </h4>
    <input type="text" id="query" name="query" placeholder="Election BUSH" maxlength="84" size="74">
    <!-- <input type="text" name="daterange" value="01/01/2015 - 01/31/2015" />  -->
      
    <script type="text/javascript">
    $(function() {
        var a = document.getElementById("daterange")
        
        $('input[name="daterange"]').daterangepicker();
    });
    </script>
    <br><br>
    
    <input type="submit" name="query1" value="Search" title= "Explore Enron email corpus">
    <input type="button" name="needhelp" value="Need help?" title="Need help?" onclick="assist()">
    <br><br>
    <div id="myDIV" style="display:None;" >           
        <iframe id="myframe"  src="default" display = "block" scrolling="auto" height="200" width="450"  title="Assisted search"></iframe>
        </div>
    
    <script>
        function assist(){
            var ifr = document.getElementById("myframe");
            var x = document.getElementById("myDIV");
            ifr.src= "Enron";
            x.style.display = "block";
        }
    </script> 

    
     
    </form>
   
    <form action="/Results"  method="POST" > 
      <h4> Your query will take few minutes to process. Please click to check status </h4>
      <br>
      <input type="submit" name="check1" value="Check Results" title = "check the status">

    </form>

  

  {% if job_meta != 'finished' %}
  
  <h4> Status of the query - {{query1}} is {{job_meta}} </h4>

  {% else %}

    {% if results|length < 1 and query1 !='' %}
      <h4> Search returned NO results </h4>
    {% elif results|length < 1 and query1 ==''%}     
        <label> Loading.. </label> 

      {% else %}


        {% for row in results %}
          <button type="button" class="collapsible">Open Email {{ row.id+1 }}</button>
          <div class="content">

            <table>
              
              <tbody></tbody>
                  <tr><td> <b> FROM </b></td><td><pre>{{ row.from_ }}</pre></td> </tr>
                  <tr><td> <b> TO </b></td><td><pre>{{ row.to}} </pre></td></tr>
                  <tr><td><b> CC </b></td><td><pre> {{row.cc}}</pre> </td></tr>
                  <tr><td> <b> BCC </b></td><td><pre> {{row.bcc}}</pre> </td></tr>
                  <tr><td> <b>  SENT_DATE </b></td><td><pre> {{row.sent_date.date()}}</pre> </td></tr>
                  <tr><td> <b> SUBJECT </b></td><td><pre>{{row.subject }}</pre></td></tr>
                  <tr><td> <b> BODY </b> </td><td><pre> {{row.body_content}} </pre></td></tr>
                  
              </tbody>

            </table>

          </div>

        {% endfor %}
    {% endif %}


  {%endif%}






<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
coll[i].addEventListener("click", function() {
  this.classList.toggle("active");
  var content = this.nextElementSibling;
  if (content.style.display === "block") {
    content.style.display = "none";
  } else {
    content.style.display = "block";
  }
});
}
</script>



 
</body>
</html>


{% endblock %}