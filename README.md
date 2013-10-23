Python Document Scripting
=========================

This project provides a general Document Scripting framework, which is like JavaScript to HTML to create dynamic websites.

	Usage: ./pbs randwalk.tex
	
How to write scripts
--------------------

* document scripts should be written as comments
* we are using Python as the scripting language.
* write scripts inside blocks denoted by, '%' is comment marker for LaTeX
		%scriptstart:python
		%scriptend	
* in between can be any python code. use _RV to denote return value (inserted
text to the document.
		_RV = []	
so inside the script block, just use
		_RV.append(string)


LaTeX Examples
--------------

### Insert an Image

Input:

```latex
%scriptstart:python
%label='fig:diff'
%width=r'0.8\linewidth'
%s=insertgraph('res/rw2d.pdf')
%_RV.append(s)
%scriptend
```

Output:

```latex
%PDS start Python Document Script generated, Do !!NOT!! modify

\begin{figure}[htpb]
\begin{centering}
\includegraphics[width=0.8\linewidth]{res/rw2d.pdf}
\end{centering}
\label{fig:diff}
\end{figure}

%PDS end
```

### Insert Images with SubCaptions and Each Row align 2 Images

Input:

```latex
%scriptstart:python
%width=r'0.45\linewidth'
%numfloatsperrow=2
%subcaptions=["First", "Second", "Third", "Fourth"]
%s=insertgraphics(['res/rw2d.pdf', 'res/rw2d.pdf', 'res/rw2d.pdf', 'res/rw2d.pdf'])
%_RV.append(s)
%scriptend
```

Output:

```latex
\begin{figure}[htpb]
\begin{centering}
\subfloat[First]{\begin{centering}
\includegraphics[width=0.45\linewidth]{res/rw2d.pdf}
\end{centering}
} \subfloat[Second]{\begin{centering}
\includegraphics[width=0.45\linewidth]{res/rw2d.pdf}
\end{centering}
}

\subfloat[Third]{\begin{centering}
\includegraphics[width=0.45\linewidth]{res/rw2d.pdf}
\end{centering}
} \subfloat[Fourth]{\begin{centering}
\includegraphics[width=0.45\linewidth]{res/rw2d.pdf}
\end{centering}
}

\end{centering}
\end{figure}
```

### Insert a table from a txt file

Input:

```latex
%scriptstart
%label='tab:res'
%caption='Numerical Results of 2D Random Walk on Rectangular Lattices'
%s=inserttable('res/numres.txt')
%_RV.append(s)
%scriptend
```

Output:

```latex
\begin{table}[htpb]
\begin{center}
\begin{tabular}{ccccccc}
\hline
$\lambda$ & $\tau$ & $D$ & $D_{mean}$ & $E$ & $D_{var}$ & $E$ \\
\hline
1 & 1 & 0.25 & 0.2493 & 0.0028 & 0.2406 & 0.0377 \\
0.5 & 0.5 & 0.125 & 0.1234 & 0.0131 & 0.131 & 0.0482 \\
0.5 & 0.5 & 0.125 & 0.1246 & 0.0035 & 0.1203 & 0.038 \\
0.2 & 0.003 & 3.3333 & 3.2938 & 0.0119 & 3.3429 & 0.0029 \\
\hline
\end{tabular}
\end{center}
\label{tab:res}
\caption{Numerical Results of 2D Random Walk on Rectangular Lattices}
\end{table}
```

