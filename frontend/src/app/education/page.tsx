"use client";

import { useEffect, useState } from "react";
import { fetchEducationCategories, fetchLesson } from "@/lib/api";

interface LessonSummary {
  id: string;
  title: string;
  difficulty: string;
  read_time: number;
}

interface Category {
  id: string;
  title: string;
  description: string;
  lesson_count: number;
  lessons: LessonSummary[];
}

interface LessonFull {
  id: string;
  title: string;
  difficulty: string;
  read_time: number;
  content: string;
  key_takeaways: string[];
}

export default function EducationPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<LessonFull | null>(null);
  const [loading, setLoading] = useState(true);
  const [lessonLoading, setLessonLoading] = useState(false);

  useEffect(() => {
    fetchEducationCategories().then((data) => {
      setCategories(Array.isArray(data) ? data : []);
      setLoading(false);
    }).catch(() => {
      setCategories([]);
      setLoading(false);
    });
  }, []);

  const openLesson = async (lessonId: string) => {
    setLessonLoading(true);
    const lesson = await fetchLesson(lessonId);
    setSelectedLesson(lesson);
    setLessonLoading(false);
  };

  const difficultyBadge = (d: string) => {
    const classes =
      d === "beginner"
        ? "bg-green-100 text-green-700"
        : d === "intermediate"
          ? "bg-blue-100 text-blue-700"
          : "bg-purple-100 text-purple-700";
    return (
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${classes}`}>
        {d.charAt(0).toUpperCase() + d.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <div className="w-8 h-8 border-2 border-dse-blue border-t-transparent rounded-full animate-spin mb-3"></div>
        Loading education content...
      </div>
    );
  }

  // Lesson detail view
  if (selectedLesson) {
    return (
      <div className="max-w-3xl mx-auto">
        <button
          onClick={() => setSelectedLesson(null)}
          className="text-dse-blue hover:text-blue-800 text-sm mb-4 inline-flex items-center gap-1 font-medium transition"
        >
          &larr; Back to lessons
        </button>

        <div className="card p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-4">
            {difficultyBadge(selectedLesson.difficulty)}
            <span className="text-sm text-gray-400">
              {selectedLesson.read_time} min read
            </span>
          </div>

          <h1 className="text-2xl font-bold mb-6 text-gray-900">{selectedLesson.title}</h1>

          <div className="prose prose-sm max-w-none text-gray-700">
            {selectedLesson.content.split("\n\n").map((para, i) => (
              <div key={i} className="mb-4">
                {para.split("\n").map((line, j) => {
                  // Handle markdown bold
                  const rendered = line.replace(
                    /\*\*(.+?)\*\*/g,
                    '<strong>$1</strong>'
                  );
                  // Handle code blocks
                  if (line.startsWith("```")) return null;
                  if (line.startsWith("- ")) {
                    return (
                      <div key={j} className="flex gap-2 ml-4 my-1">
                        <span className="text-dse-blue">&#8226;</span>
                        <span
                          dangerouslySetInnerHTML={{ __html: rendered.slice(2) }}
                        />
                      </div>
                    );
                  }
                  if (/^\d+\./.test(line)) {
                    return (
                      <div key={j} className="flex gap-2 ml-4 my-1">
                        <span
                          dangerouslySetInnerHTML={{ __html: rendered }}
                        />
                      </div>
                    );
                  }
                  return (
                    <p
                      key={j}
                      dangerouslySetInnerHTML={{ __html: rendered }}
                      className={
                        rendered.includes("<strong>") && !line.startsWith("- ")
                          ? "font-medium"
                          : ""
                      }
                    />
                  );
                })}
              </div>
            ))}
          </div>

          {/* Key Takeaways */}
          <div className="mt-8 bg-dse-blue text-white rounded-xl p-5">
            <h3 className="font-semibold text-lg mb-3">Key Takeaways</h3>
            <ul className="space-y-2">
              {selectedLesson.key_takeaways.map((t, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-dse-gold mt-0.5">&#10003;</span>
                  <span>{t}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  }

  // Category listing view
  return (
    <div>
      <h1 className="page-heading">Investment Education</h1>
      <p className="page-subtitle mb-6">
        Learn about investing on the Dar es Salaam Stock Exchange. From basics to
        advanced strategies.
      </p>

      {/* Progress overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="card p-4 text-center border-l-4 border-green-500">
          <div className="text-2xl font-bold text-green-700">
            {categories.reduce((s, c) => s + c.lesson_count, 0)}
          </div>
          <div className="text-xs text-green-600 font-medium">Total Lessons</div>
        </div>
        <div className="card p-4 text-center border-l-4 border-blue-500">
          <div className="text-2xl font-bold text-blue-700">
            {categories.length}
          </div>
          <div className="text-xs text-blue-600 font-medium">Categories</div>
        </div>
        <div className="card p-4 text-center border-l-4 border-purple-500">
          <div className="text-2xl font-bold text-purple-700">
            {categories.reduce(
              (s, c) =>
                s +
                c.lessons.filter((l) => l.difficulty === "beginner").length,
              0
            )}
          </div>
          <div className="text-xs text-purple-600 font-medium">Beginner Lessons</div>
        </div>
        <div className="card p-4 text-center border-l-4 border-amber-500">
          <div className="text-2xl font-bold text-amber-700">
            {categories.reduce(
              (s, c) => s + c.lessons.reduce((a, l) => a + l.read_time, 0),
              0
            )}
          </div>
          <div className="text-xs text-amber-600 font-medium">Total Minutes</div>
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-8">
        {categories.map((cat) => (
          <div key={cat.id}>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold text-gray-900">{cat.title}</h2>
              <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-medium">
                {cat.lesson_count} lessons
              </span>
            </div>
            <p className="text-gray-500 text-sm mb-4">{cat.description}</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {cat.lessons.map((lesson) => (
                <button
                  key={lesson.id}
                  onClick={() => openLesson(lesson.id)}
                  className="card p-5 text-left hover:shadow-md transition-all hover:border-dse-blue group"
                >
                  <div className="flex items-center justify-between mb-2">
                    {difficultyBadge(lesson.difficulty)}
                    <span className="text-xs text-gray-400">
                      {lesson.read_time} min
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900">{lesson.title}</h3>
                  <div className="text-sm text-dse-blue mt-2 group-hover:translate-x-1 transition-transform">
                    Read lesson &rarr;
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {lessonLoading && (
        <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="card p-8 shadow-xl flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-dse-blue border-t-transparent rounded-full animate-spin"></div>
            Loading lesson...
          </div>
        </div>
      )}
    </div>
  );
}
