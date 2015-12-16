import math as m

for x in [.1, .3, .45, .55, .7, .9]:  # Sklierung zum Zeichnen 10*
    print("\draw[->, bend angle=45, bend right, blue] (%.2f,0) to (%.2f,0);"
          % (10*x, x*5))  # Linkskante
    print("\draw[->, bend angle=60, bend right, red] (%.2f,0) to (%.2f,0);"
          % (10*x, 10*(x*.5+.5)))  # Rechtskante
    y = m.modf(2*x)
    print("\draw[->, bend angle=30, bend right, green] (%.2f,0) to (%.2f,0);"
          % (10*x, 10*y[0]))  # Rueckwaertskante
