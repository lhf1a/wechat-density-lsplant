#!/usr/bin/env python3
"""Run production class-name resolution with old/new/isolated Tinker loader fixtures.

Requires JDK 17+. This tests class selection, not LSPlant or Android UI behavior.
An optional source path permits the same baseline/modified/rollback regression.
"""
import sys, subprocess, tempfile
from pathlib import Path
source=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('Hooks.java');s=source.read_text()
if 'static Class<?> resolveDensity(' in s:
 start=s.index('    static Class<?> resolveDensity(');end=s.index('    static void install(Context c)',start)
 method=s[start:end]
 assert 'install(context, resolveDensity((ClassLoader) args[0]))' in s
 assert 'resolved != null ? resolved : resolveDensity(c.getClassLoader())' in s
else:
 assert s.count('Class.forName("jf5.f", false,')==2
 method='static Class<?> resolveDensity(ClassLoader loader) throws ClassNotFoundException {return Class.forName("jf5.f", false, loader);}'
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp)
 for pkg in ['jf5','bf5']:
  f=p/pkg/pkg/'f.java';f.parent.mkdir(parents=True);f.write_text('package '+pkg+'; public class f { static { System.setProperty("density.fixture.initialized", "yes"); } }')
  subprocess.run(['javac','--release','8','-d',str(p/pkg),str(f)],check=True)
 (p/'empty').mkdir()
 java=r"""import java.net.*;import java.io.*;
 public class LookupTest {
 METHOD
 static ClassLoader loader(String p)throws Exception{return new URLClassLoader(new URL[]{new File(p).toURI().toURL()},null);}
 public static void main(String[] a)throws Exception{
 boolean ok=true;
 System.out.println("old="+resolveDensity(loader(a[0])).getName());
 try{Class<?> base=resolveDensity(loader(a[1]));Class<?> patch=resolveDensity(loader(a[1]));
 System.out.println("new="+base.getName());System.out.println("tinker_distinct="+(base!=patch));ok &= base!=patch;}
 catch(ClassNotFoundException e){System.out.println("new=MISSING tinker=MISSING");ok=false;}
 try{resolveDensity(loader(a[2]));System.out.println("unknown=ACCEPTED");ok=false;}
 catch(ClassNotFoundException e){System.out.println("unknown=REJECTED");}
 boolean deferred=System.getProperty("density.fixture.initialized")==null;
 System.out.println("initialization_deferred="+deferred);ok &= deferred;
 if(!ok)System.exit(1);
 }}""".replace('METHOD',method)
 (p/'LookupTest.java').write_text(java)
 subprocess.run(['javac','--release','8',str(p/'LookupTest.java')],check=True)
 r=subprocess.run(['java','-cp',str(p),'LookupTest',str(p/'jf5'),str(p/'bf5'),str(p/'empty')])
 sys.exit(r.returncode)
