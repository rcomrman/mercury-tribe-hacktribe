"""QEMU debugger metadata breakpoints; never sends memory-write packets."""
import socket,struct,time
class RSP:
 def __init__(self,port):
  for _ in range(100):
   try:self.s=socket.create_connection(('127.0.0.1',port),.2);break
   except OSError:time.sleep(.02)
  else:raise RuntimeError('stub connection')
  self.s.settimeout(8);self.commands=[]
 def packet(self):
  while self.s.recv(1)!=b'$':pass
  b=b''
  while True:
   c=self.s.recv(1)
   if not c:raise EOFError()
   if c==b'#':break
   b+=c
  checksum=self.s.recv(2);assert int(checksum,16)==sum(b)%256
  self.s.sendall(b'+');return b.decode()
 def cmd(self,s):
  assert not s.startswith(('M','X')), 'no memory writes'
  self.commands.append(s.split(',')[0] if not s.startswith('G') else 'G<registers>')
  b=s.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode());return self.packet()
 def bp(self,a,on=True):assert self.cmd(f'{"Z" if on else "z"}0,{a:x},4')=='OK'
 def mem(self,a,n=4):return self.cmd(f'm{a:x},{n:x}')
 def regs(self):return self.cmd('g')
 def resume(self):return self.cmd('c')
 def inject(self,action,entry,ret,stack):
  saved=self.regs();b=bytearray.fromhex(saved)
  for i,v in {0:action,13:stack,14:ret,15:entry}.items():struct.pack_into('<I',b,i*4,v)
  self.bp(ret);assert self.cmd('G'+b.hex())=='OK';stop=self.resume();assert stop.startswith(('T05','S05')),stop
  self.bp(ret,False);assert self.cmd('G'+saved)=='OK';assert self.regs()==saved
  return {'register_restore_exact':True,'saved_core':list(struct.unpack_from('<16I',bytes.fromhex(saved)))}
