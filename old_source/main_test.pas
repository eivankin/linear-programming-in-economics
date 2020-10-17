program GMRZLP;

uses
graphABC;

const
  W = 800; H = 650;

function L(x11, x22, a11, a22: integer): integer;//Целевая функция для проверок max/min
begin
  L := a11 * x11 + a22 * x22; 
end;

function F(x: real; a1, a2, b1: integer): real;//Линейные ограничения для построений
begin
  F := (b1 - a1 * x) / a2; 
end;

var
  x0, y0, x, y, xLeft, yLeft, xRight, yRight, n, a1, a2, b1, a11, a22, maxL, maxX1, maxX2, x11, x22, index, ve, tmp: integer;
  a, b, fmin, fmax, {x1, y1,} mx, my, dx, dy, num: real;
  k, n1, n2, minx1, minx2: byte;
  s{для засечек}, s1, s4, s0: string;
//  z: text;

begin
  val(ParamStr(1), ve, tmp);
  val(ParamStr(2), index, tmp);
  if tmp>0 then exit;
  SetWindowPos(550, 0);
  Window.Title := 'Графический метод решения задач линейного программирования';
  setbrushcolor(clWhite);
  setwindowsize(W, H);
  SetFontSize(12);
//  assign(z, 'output.txt');
//  reset(z);
//  readln(z, val);
//  readln(z, index);
//  close(z);
  assign(input, 'input.txt');
  for var j := 1 to ve do 
  begin
    clearwindow;
    TextOut(35, 0, 'Математическая модель задачи:');
    readln(input, a11, a22, n1);//n1=0 - min, n1=1 - max
    case n1 of
      0:
        begin
          s0 := '>=';
          s4 := 'Минимальное';
        end;
      1: 
        begin
          s0 := '<=';
          s4 := 'Максимальное';
        end
    else exit;
    end; 
    TextOut(35, 20, 'L=' + a11 + '*x1+' + a22 + '*x2->' + s4);
    readln(input, k);
    readln(input, minx1, minx2);//Кол-во линейных ограничений
    xLeft := 50;
    yLeft := 170;
    xRight := W - 50;
    yRight := H - 40;
    a := 0; b := 10 * (floor(b1 / 10) + 1); dx := 1;
    fmin := 0; fmax := 10 * (floor(b1 / 10) + 1); dy := 1;
    mx := (xRight - xLeft) / (b - a); //масштаб по Х
    my := (yRight - yLeft) / (fmax - fmin); //масштаб по Y
    //начало координат:
    x0 := trunc(abs(a) * mx) + xLeft;
    y0 := yRight - trunc(abs(fmin) * my);
    //Рисуем оси координат:
    line(xLeft, y0, xRight + 10, y0);
    line(x0, yLeft - 10, x0, yRight);
    SetFontSize(12);
    SetFontColor(clRed);
    TextOut(xRight + 20, y0 - 15, 'X');
    TextOut(x0 - 10, yLeft - 30, 'Y');
    SetFontSize(8);
    SetFontColor(clBlack);
    { Засечки по оси OX: }
    n := round((b - a) / dx) + 1;
    for var i := 1 to n do
    begin
      num := a + (i - 1) * dx; 
      x := xLeft + trunc(mx * (num - a)); 
      Line(x, y0 - 3, x, y0 + 3); 
      str(Num, s);
      if abs(num) > 1E-15 then 
        TextOut(x - TextWidth(s) div 2, y0 + 10, s)
    end;
    { Засечки на оси OY: }
    n := round((fmax - fmin) / dy) + 1; 
    for var i := 1 to n do
    begin
      num := fMin + (i - 1) * dy; 
      y := yRight - trunc(my * (num - fmin));
      Line(x0 - 3, y, x0 + 3, y); 
      str(num:0:0, s);
      if abs(num) > 1E-15 then 
        TextOut(x0 - 17, y - TextHeight(s) div 2, s)
    end;
    TextOut(x0 - 10, y0 + 10, '0');
    setfontsize(12);
    SetPenWidth(2);
    line(40, 52, 40, 40 + 23 * k div 2 - 4);
    arc(45, 52, 5, 180, 90);
    arc(35, 40 + 23 * k div 2 - 5, 5, 270, 360);
    arc(35, 40 + 23 * k div 2 + 5, 5, 0, 90);
    line(40, 40 + 23 * k div 2 + 4, 40, 40 + 23 * k - 4);
    arc(45, 40 + 23 * k - 5, 5, 180, 270);
    SetPenWidth(1);
    if minx1 > 0 then line(x0 + round(minx1 * mx), y0, x0 +  round(minx1 * mx), yLeft - 10, clGreen);
    if minx2 > 0 then line(xLeft, y0 - round(minx2 * mx), xRight - 10, y0 - round(minx2 * mx), clGreen);
    for var i := 1 to k do
    begin
//      x1 := a; 
      readln(input, a1, a2, b1);
      TextOut(45, 30 + 20 * i, a1 + '*x1+' + a2 + '*x2' + s0 + b1);
      line(x0, y0 - round(b1 / a2 * my), x0 + round(b1 / a1 * mx), y0, clGreen);
//      while x1 <= b do
//      begin
//        y1 := F(x1, a1, a2, b1); 
//        x := x0 + round(x1 * mx); 
//        y := y0 - round(y1 * my);
//        if (y >= yLeft) and (y <= yRight) then SetPixel(x, y, clGreen);
//        x1 := x1 + 0.01;
//      end;
    end;
    if n1 = 1 then floodfill(x0 + 1, y0 - 1, clBlue)
    else begin
      line(x0 + round(minx1 * mx), yLeft - 10, xRight + 10, yLeft - 10, clBlue);
      line(xRight + 10, y0, xRight + 10, yLeft - 10, clBlue);
      floodfill(xRight + 9, yLeft - 9, clBlue);
    end;
    SetFontSize(12);
    //TextOut(35, H - 100, 'Введите кол-во вершин многоугольника решений, укажите их координаты');
    readln(input, n2);
    //setlength(L1, n2 + 1); setlength(K1, n2 + 1); setlength(K2, n2 + 1);
    readln(input, x11, x22);
    if (x11 > 0) and (x22 > 0) then begin
      line(x0 + round(x11 * mx), y0, x0 +  round(x11 * mx), y0 - round(x22 * my), clOrange);
      line(x0, y0 - round(x22 * my), x0 + round(x11 * mx), y0 - round(x22 * my), clOrange);
    end;
    maxX1 := x11;
    maxX2 := x22;
    maxL := L(x11, x22, a11, a22);
    for var i := 1 to n2 - 1 do  
    begin
      readln(x11, x22);
      if (x11 > 0) and (x22 > 0) then begin//пепрендикуляры к точкам пересечения
        line(x0 + round(x11 * mx), y0, x0 +  round(x11 * mx), y0 - round(x22 * my), clOrange);
        line(x0, y0 - round(x22 * my), x0 + round(x11 * mx), y0 - round(x22 * my), clOrange);
      end;
      if (n1 = 1) and (L(x11, x22, a11, a22) > maxL) then begin//поиск значения ЦФ
        maxL := L(x11, x22, a11, a22);
        maxX1 := x11;
        maxX2 := x22;
      end
      else if (n1 = 0) and (L(x11, x22, a11, a22) < maxL) then begin
        maxL := L(x11, x22, a11, a22);
        maxX1 := x11;
        maxX2 := x22;
      end;
    end;
    line(x0, y0 - round(maxL / a22 * my), x0 + round(maxL / a11 * mx), y0, clRed); //линия ЦФ
    s1 := 'Оптимальное решение задачи: x1=' + maxX1 + '; x2=' + maxX2 + ';';
    s4 += ' значение функции: L=' + maxL + '.';
    TextOut(350, 0, s1);
    TextOut(350, 20, s4);
    savewindow('solve' + j + '.bmp');
    sleep(6000);
  end;
  close(input);
  readln();
  CloseWindow;
end.