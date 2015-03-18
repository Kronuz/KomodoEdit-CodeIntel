#!/usr/bin/env python
import os

from setuptools import setup, Extension


########################################################################
# SilverCity (it's in PyPI, but unpatched, this one is patched)

silvercity_src_files = []

silvercity_src = 'silvercity_src/PySilverCity/Src'

# Add Python extension source files
silvercity_src_files.extend([
    os.path.join(silvercity_src, file) for file in [
        'PyLexerModule.cxx',
        'PyPropSet.cxx',
        'PySilverCity.cxx',
        'PyWordList.cxx',
    ]
])

silvercity_libsrc = 'silvercity_src/Lib/Src'

# Add library source files
silvercity_src_files.extend([
    os.path.join(silvercity_libsrc, file) for file in [
        'BufferAccessor.cxx',
        'LexState.cxx',
        'LineVector.cxx',
        'SC_PropSet.cxx',
        'Platform.cxx',
    ]
])

# Add Scintilla support files
scintilla_include = 'scintilla/include'
scintilla_src = 'scintilla/src'
scintilla_lexlib = 'scintilla/lexlib'
scintilla_lexers = 'scintilla/lexers'

silvercity_src_files.extend([
    os.path.join(scintilla_src, file) for file in [
        'KeyMap.cxx',
        'Catalogue.cxx',
        'UniConversion.cxx',
    ]
])

silvercity_src_files.extend([
    os.path.join(scintilla_lexlib, file) for file in [
        'WordList.cxx',
        'PropSetSimple.cxx',
        'Accessor.cxx',
        'CharacterCategory.cxx',
        'CharacterSet.cxx',
        'LexerBase.cxx',
        'LexerNoExceptions.cxx',
        'LexerSimple.cxx',
        'LexerModule.cxx',
        'StyleContext.cxx',
    ]
])

# Add Scintilla lexers
for file in os.listdir(scintilla_lexers):
    file = os.path.join(scintilla_lexers, file)
    if os.path.basename(file).startswith('Lex') and \
       os.path.splitext(file)[1] == '.cxx':
        silvercity_src_files.append(file)

silvercity_include_dirs = [
    scintilla_src,
    scintilla_lexlib,
    scintilla_lexers,
    scintilla_include,
    silvercity_src,
    silvercity_libsrc,
]

silvercity_ext = Extension(
    '_SilverCity',
    silvercity_src_files,
    include_dirs=silvercity_include_dirs,
    libraries=['pcre'],
)

########################################################################
# sgmlop (it's in PyPI but as an external)

sgmlop_include_dirs = [
    'sgmlop',
]
sgmlop_ext = Extension(
    'sgmlop', [
        'sgmlop/sgmlop.c',
    ],
    include_dirs=sgmlop_include_dirs,
)

########################################################################
# cElementTree (it's in PyPI, but unpatched, this one is patched)

celementtree_include_dirs = [
    'cElementTree',
    'cElementTree/expat',
]
celementtree_ext = Extension(
    'cElementTree', [
        'cElementTree/cElementTree.c',
        'cElementTree/expat/xmlparse.c',
        'cElementTree/expat/xmlrole.c',
        'cElementTree/expat/xmltok.c',
    ],
    define_macros=[
        ('XML_STATIC', None),
        ('HAVE_MEMMOVE', "1"),
    ],
    include_dirs=celementtree_include_dirs,
)

########################################################################
# ciElementTree (it's not in PyPI)

cielementtree_include_dirs = [
    'ciElementTree',
    'ciElementTree/expat',
]
cielementtree_ext = Extension(
    'ciElementTree', [
        'ciElementTree/cElementTree.c',
        'ciElementTree/expat/xmlparse.c',
        'ciElementTree/expat/xmlrole.c',
        'ciElementTree/expat/xmltok.c',
    ],
    define_macros=[
        ('XML_STATIC', None),
        ('HAVE_MEMMOVE', "1"),
    ],
    include_dirs=cielementtree_include_dirs,
)

########################################################################
# codeintel

setup(
    name="CodeIntel",
    version="0.1.1",
    description="Komodo Edit CodeIntel",
    author="Komodo Edit Team",
    author_email="german.mb@gmail.com",
    license="GPL",
    classifiers=[
        # License should match "license" above.
        "License :: OSI Approved :: GNU General Public License (GPL)",
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=[
        'six',
        'zope.cachedescriptors',
        'subprocess32',
        'inflector',
    ],
    ext_modules=[
        silvercity_ext,
        celementtree_ext,
        cielementtree_ext,
        sgmlop_ext,
    ],
    entry_points={
        'console_scripts': ['codeintel = codeintel:main'],
    },
    packages=[
        'codeintel',
        'codeintel2',
        'codeintel2.oop',
        'codeintel2.database',
        'elementtree',
        'SilverCity',
    ],
    package_data={'codeintel2': [
        'catalogs/*.cix',
        'stdlibs/*.cix',
        'lexers/*.lexres',
    ]},
)
