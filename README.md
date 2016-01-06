# uploadr

XEP-0363 CLI upload tool

## Installation

1. Checkout uploadr

        git clone https://github.com/sezuan/uploadr.git

2. Install Python dependencies (all Python versions)

        cd uploadr/
        virtualenv python
        . python/bin/activate
        pip install requests dnspython pyasn1 pyasn1_modules

3. Install Python dependencies (Python < 2.7.9, to avoid SSL errors))

        pip install pyopenssl ndg-httpsclient

4. Install SleekXMPP with XEP-0363 plugin

        git clone https://github.com/sezuan/SleekXMPP.git -b xep_0363
        pushd SleekXMPP
        pip install .
        popd

## Usage

    $ ./uploadr.py
    usage: uploadr.py [-h] -j JID -p PASSWORD filename

You can put your credentials into ~/.uploadrc

    cat > ~/.uploadrc << EOF
    matze@jebbar.foo
    89Y7UyQyKUDDU
    EOF
    chmod 400 ~/.uploadrc

