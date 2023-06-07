import math
from flask import Flask, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor


conn = psycopg2.connect(
    "host=db dbname=postgres user=postgres password=postgres",
    cursor_factory=RealDictCursor)
app = Flask(__name__)


@app.route("/")
def hello_world():
    name = request.args.get("name", "World")
    return f"<p>Hello, {name}!</p>"



@app.route("/sets")
def render_sets():
    set_name = request.args.get("set_name", "")
    theme_name = request.args.get("theme_name", "")
    part_count_from = int(request.args.get("part_count_from") or 0)
    part_count_to = int(request.args.get("part_count_to") or 10000)
    
    page_count = int(request.args.get("page") or 1)
    limit = int(request.args.get("limit") or 10)
    offset = int(request.args.get("offset") or 1)
    results_per_page = int(request.args.get('results_per_page') or 50)
    sort_by = request.args.get("sort_by", "set_num")
    sort_dir = request.args.get("sort_dir", default = 'asc')
    
    from_where_clause = """
    from set s
    inner join theme t on s.theme_id = t.id
    where s.name ilike %(set_name)s and
    t.name ilike %(theme_name)s and
    s.num_parts >= %(part_count_from)s and s.num_parts <= %(part_count_to)s
    """

    if sort_dir == "desc":
        order_by_clause = f"order by {sort_by} desc"
    else:
        order_by_clause = f"order by {sort_by} asc"
    
    limit_clause = f"limit %(limit)s"

    offset_clause = f"offset ( (%(offset)s -1) * {results_per_page})"

    params = {
        "set_name": f"%{set_name}%",
        "theme_name": f"%{theme_name}%",
        "part_count_from": part_count_from,
        "part_count_to": part_count_to,
        "limit": limit,
        "offset": offset,
        "results_per_page": results_per_page
    }


    with conn.cursor() as cur:
        cur.execute(f"select s.set_num as set_num, s.name as set_name, s.year as year, t.name as theme_name, s.num_parts as parts_count{from_where_clause} {order_by_clause} {limit_clause} {offset_clause}",
                    params)
        results = list(cur.fetchall())

        cur.execute(f"select count(*) as count {from_where_clause}",
                    params)
        count = cur.fetchone()["count"]

        total_pages = math.ceil(count / results_per_page)

    

        return render_template("sets.html",
                               params=request.args,
                               result_count=count,
                               sets=results,
                               sort_by=sort_by,
                               sort_dir=sort_dir,
                               limit=limit,
                               offset=offset,
                               results_per_page = results_per_page,
                               total_pages = total_pages)
    