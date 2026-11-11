Name:		istack-commons-runtime
Version:	4.1.2
Release:	1
Summary:	istack common utility code
Group:		Development/Java
License:	BSD-3-Clause
URL:		https://github.com/eclipse-ee4j/jaxb-istack-commons
Source0:	https://github.com/eclipse-ee4j/jaxb-istack-commons/archive/refs/tags/%{version}.tar.gz#/istack-commons-runtime-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(jakarta.activation:jakarta.activation-api)

%description
istack-commons-runtime %{version} is the small utility library JAXB uses
for data sources, localization, and logging. ByteArrayDataSource implements
jakarta.activation.DataSource.

%prep
%autosetup -n jaxb-istack-commons-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
find istack-commons/runtime/src/main/java -name '*.java' \
	! -name 'module-info.java' > sources.list
test "$(wc -l < sources.list)" -eq 20
mkdir -p classes
javac --release 11 -encoding UTF-8 \
	-cp %{_javadir}/jakarta.activation-api.jar \
	-d classes @sources.list
jar cf istack-commons-runtime.jar -C classes .
jar tf istack-commons-runtime.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
javap -verbose -cp istack-commons-runtime.jar com.sun.istack.ByteArrayDataSource | grep -F 'major version: 55'

cat > istack-commons-runtime.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.sun.istack</groupId>
  <artifactId>istack-commons-runtime</artifactId>
  <version>4.1.2</version>
  <name>istack common utility code runtime</name>
  <description>istack common utility code runtime</description>
  <licenses>
    <license>
      <name>BSD-3-Clause</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>jakarta.activation</groupId>
      <artifactId>jakarta.activation-api</artifactId>
      <version>2.1.3</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact istack-commons-runtime.pom:istack-commons-runtime.jar \
	--file-name istack-commons-runtime \
	--filelist .mfiles

%check
mkdir -p check
cat > check/Smoke.java << 'END'
import com.sun.istack.ByteArrayDataSource;
public class Smoke {
	public static void main(String[] args) throws Exception {
		byte[] buf = new byte[] {104, 105};
		ByteArrayDataSource source = new ByteArrayDataSource(buf, "text/plain");
		int first = source.getInputStream().read();
		System.out.println("istack_ok " + source.getContentType() + " " + first);
	}
}
END
JAR=%{buildroot}%{_javadir}/istack-commons-runtime.jar
test -f "$JAR"
javac --release 11 -encoding UTF-8 \
	-cp "$JAR:%{_javadir}/jakarta.activation-api.jar" \
	-d check check/Smoke.java
java -cp "check:$JAR:%{_javadir}/jakarta.activation-api.jar" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'istack_ok text/plain 104' check/out.txt

%files -f .mfiles
%doc LICENSE.md NOTICE.md
