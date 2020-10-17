uses FormsABC;

var
  n := new IntegerField('Кол-во задач:', 120);
  f2 := new FlowBreak;
  cb := new ComboBox;
  f1 := new FlowBreak;
  sp := new space(15);
  ok := new Button('Запустить');

procedure p();
var args: string;
begin
  args:=n.Value+' '+cb.SelectedIndex;
  MainForm.Close;
  exec('main_test.exe', args);
  exit;
end;

begin
  MainForm.Height := 150;
  MainForm.Width := 140;
  MainForm.Title := 'Графический метод решения задач линейного программирования';
  n.Value := 1;
  cb.Items.Add('Ввод из input.txt');
  cb.Items.Add('Ввод вручную');
  ok.Click += p;
end.