import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Sparkles } from 'lucide-react';
import { fetchApi } from '../lib/api';

const DEFAULT_QUESTIONS = [
  'Son haftalarda hangi fabrikalar Avrupa\'da taşındı?',
  'Otomotiv sektöründe en son yatırım haberleri neler?',
  'Hangi şirketler yeni tesis açıyor?',
  'Türkiye\'deki endüstriyel gelişmeler neler?',
  'Almanya\'da fabrika kapanışları var mı?',
  'En yüksek BIOS skorlu haberler hangileri?',
];

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Merhaba! Ben Synapse. Aşağıdaki önerilerden birini seçin ya da kendi sorunuzu yazın.' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [autoQuestions, setAutoQuestions] = useState(DEFAULT_QUESTIONS);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchApi('/rag/suggested-questions').then((res) => {
      const qs = res.questions || [];
      if (qs.length > 0) {
        setAutoQuestions([...qs.slice(0, 3), ...DEFAULT_QUESTIONS.slice(0, 3)]);
      }
    }).catch(() => {});
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const sendMessage = (text) => {
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');
    setShowSuggestions(false);
    setIsTyping(true);
    (async () => {
      try {
        const res = await fetchApi('/rag/ask', {
          method: 'POST',
          body: JSON.stringify({ question: text, mode: 'genel' }),
        });
        const reply = res.answer_tr || 'Cevap üretilemedi.';
        setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      } catch (err) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Şu an AI servisine ulaşılamıyor. Lütfen daha sonra tekrar deneyin.',
        }]);
      } finally {
        setIsTyping(false);
      }
    })();
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    sendMessage(input.trim());
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 p-4 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-[0_8px_30px_rgba(79,70,229,0.4)] hover:shadow-[0_8px_30px_rgba(79,70,229,0.6)] transform hover:-translate-y-1 transition-all z-50 flex items-center justify-center ${isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}`}
      >
        <MessageSquare className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      <div className={`fixed bottom-4 right-4 w-[92vw] max-w-sm md:max-w-md bg-card/95 backdrop-blur-xl border border-border/60 rounded-2xl shadow-2xl flex flex-col z-50 transform transition-all duration-300 origin-bottom-right ${isOpen ? 'scale-100 opacity-100' : 'scale-0 opacity-0 pointer-events-none'}`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border/50 bg-primary/5 rounded-t-2xl">
          <div className="flex items-center gap-2">
            <div className="bg-primary/20 p-1.5 rounded-lg">
              <Bot className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-foreground">Synapse</h3>
              <p className="text-[10px] text-primary flex items-center gap-1"><Sparkles className="w-3 h-3"/> AI Asistan</p>
            </div>
          </div>
          <button onClick={() => setIsOpen(false)} className="p-1 text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 overflow-y-auto min-h-[260px] max-h-[55vh] space-y-4 custom-scrollbar">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-br-sm' : 'bg-secondary text-secondary-foreground rounded-bl-sm border border-border/50'}`}>
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}

          {/* Otomatik önerilen sorular */}
          {showSuggestions && messages.length === 1 && (
            <div className="space-y-1.5">
              <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider pl-1">Önerilen Sorular</p>
              {autoQuestions.slice(0, 4).map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="w-full text-left text-xs px-3 py-2 rounded-xl bg-primary/5 border border-primary/15 text-primary hover:bg-primary/10 transition-colors font-medium"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-secondary text-secondary-foreground rounded-2xl rounded-bl-sm border border-border/50 px-4 py-3 text-sm flex gap-1">
                <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce"></span>
                <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-3 border-t border-border/50 bg-background/50 rounded-b-2xl">
          <form onSubmit={handleSend} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Örn: Otomotiv sektörü özeti ver..."
              className="flex-1 bg-card border border-border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all shadow-sm"
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="bg-primary text-primary-foreground p-2.5 rounded-xl disabled:opacity-50 hover:bg-primary/90 transition-colors shadow-sm"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

      </div>
    </>
  );
}
