import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiBookOpen, FiPlayCircle, FiCheckCircle, FiPlusCircle, FiLoader } from 'react-icons/fi';
import { courseService } from '../../services/courseService';

const Courses = () => {
    const [availableCourses, setAvailableCourses] = useState([]);
    const [myCourses, setMyCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('enrolled');

    const loadData = async () => {
        setLoading(true);
        try {
            const [avail, enrolled] = await Promise.all([
                courseService.getAvailableCourses(),
                courseService.getMyCourses()
            ]);
            setAvailableCourses(avail);
            setMyCourses(enrolled);
        } catch (err) {
            console.error("Failed to load courses:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleEnroll = async (courseId) => {
        try {
            await courseService.enroll(courseId);
            loadData();
            setActiveTab('enrolled');
        } catch (err) {
            console.error("Failed to enroll", err);
            alert("Failed to enroll. You might already be enrolled.");
        }
    };

    const handleToggleProgress = async (courseId, lessonId, currentStatus) => {
        const newStatus = currentStatus === 'completed' ? 'not_started' : 'completed';
        try {
            await courseService.updateProgress(courseId, lessonId, newStatus);
            loadData();
        } catch (err) {
            console.error("Failed to update progress", err);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <FiLoader className="animate-spin text-4xl text-blue-500" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4 mb-6">
                <button 
                    onClick={() => setActiveTab('enrolled')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'enrolled' ? 'bg-blue-600 text-white' : 'bg-gray-50 text-gray-600 hover:text-gray-900'}`}
                >
                    My Enrolled Courses
                </button>
                <button 
                    onClick={() => setActiveTab('explore')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'explore' ? 'bg-blue-600 text-gray-900' : 'bg-gray-50 text-gray-600 hover:text-gray-900'}`}
                >
                    Explore Courses
                </button>
            </div>

            {activeTab === 'explore' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {availableCourses.map(course => (
                        <div key={course.id} className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm group">
                            <div className="h-40 bg-gray-50 relative overflow-hidden">
                                {course.thumbnail_url ? (
                                    <img src={course.thumbnail_url} alt={course.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center">
                                        <FiBookOpen className="text-4xl text-slate-600" />
                                    </div>
                                )}
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 to-transparent" />
                            </div>
                            <div className="p-6">
                                <h3 className="text-xl font-bold text-gray-900 mb-2">{course.title}</h3>
                                <p className="text-sm text-gray-600 mb-6 line-clamp-2">{course.description}</p>
                                <button 
                                    onClick={() => handleEnroll(course.id)}
                                    className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
                                >
                                    <FiPlusCircle /> Enroll Now
                                </button>
                            </div>
                        </div>
                    ))}
                    {availableCourses.length === 0 && <p className="text-gray-600">No courses available.</p>}
                </div>
            )}

            {activeTab === 'enrolled' && (
                <div className="space-y-6">
                    {myCourses.map(enrollment => {
                        const course = enrollment.course;
                        const totalLessons = course.lessons.length;
                        const completedLessons = enrollment.progress.filter(p => p.status === 'completed').length;
                        const progressPct = totalLessons === 0 ? 0 : Math.round((completedLessons / totalLessons) * 100);

                        return (
                            <div key={enrollment.id} className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                                <div className="flex flex-col md:flex-row gap-6">
                                    {/* Thumbnail */}
                                    <div className="w-full md:w-64 h-40 bg-gray-50 rounded-xl overflow-hidden shrink-0">
                                        {course.thumbnail_url ? (
                                            <img src={course.thumbnail_url} alt={course.title} className="w-full h-full object-cover" />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center"><FiBookOpen className="text-4xl text-slate-600" /></div>
                                        )}
                                    </div>
                                    
                                    {/* Content */}
                                    <div className="flex-1 flex flex-col justify-between">
                                        <div>
                                            <h2 className="text-2xl font-bold text-gray-900 mb-2">{course.title}</h2>
                                            <p className="text-gray-600 text-sm mb-4">{course.description}</p>
                                        </div>
                                        
                                        {/* Progress Bar */}
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm font-medium">
                                                <span className="text-gray-700">Overall Progress</span>
                                                <span className="text-blue-400">{progressPct}%</span>
                                            </div>
                                            <div className="w-full h-2.5 bg-gray-50 rounded-full overflow-hidden">
                                                <div 
                                                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-1000"
                                                    style={{ width: `${progressPct}%` }}
                                                />
                                            </div>
                                            <p className="text-xs text-gray-600 mt-1">{completedLessons} of {totalLessons} lessons completed</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Lessons List */}
                                <div className="mt-8 border-t border-gray-200 pt-6">
                                    <h3 className="text-lg font-bold text-gray-900 mb-4">Course Lessons</h3>
                                    <div className="space-y-3">
                                        {course.lessons.map((lesson, idx) => {
                                            const prog = enrollment.progress.find(p => p.lesson_id === lesson.id);
                                            const isCompleted = prog?.status === 'completed';
                                            
                                            return (
                                                <div key={lesson.id} className="flex items-center justify-between p-4 bg-gray-100 hover:bg-gray-50 rounded-xl transition-colors border border-gray-200/50">
                                                    <div className="flex items-center gap-4">
                                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${isCompleted ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-100 text-gray-600'}`}>
                                                            {idx + 1}
                                                        </div>
                                                        <div>
                                                            <h4 className={`font-medium ${isCompleted ? 'text-gray-700 line-through opacity-75' : 'text-white'}`}>{lesson.title}</h4>
                                                            {lesson.video_url && <span className="text-xs text-blue-400 flex items-center gap-1 mt-1"><FiPlayCircle /> Video Available</span>}
                                                        </div>
                                                    </div>
                                                    <button 
                                                        onClick={() => handleToggleProgress(course.id, lesson.id, prog?.status || 'not_started')}
                                                        className={`p-2 rounded-lg border transition-colors ${isCompleted ? 'border-emerald-500/50 text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20' : 'border-gray-300 text-gray-600 hover:text-gray-900 hover:border-slate-400'}`}
                                                    >
                                                        <FiCheckCircle size={20} />
                                                    </button>
                                                </div>
                                            );
                                        })}
                                        {course.lessons.length === 0 && <p className="text-gray-600 text-sm">No lessons found in this course.</p>}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                    {myCourses.length === 0 && (
                        <div className="text-center py-12 bg-white rounded-2xl border border-gray-200">
                            <FiBookOpen className="text-6xl text-slate-700 mx-auto mb-4" />
                            <h3 className="text-xl font-bold text-gray-900 mb-2">No Enrolled Courses</h3>
                            <p className="text-gray-600 mb-6">You haven't enrolled in any courses yet.</p>
                            <button onClick={() => setActiveTab('explore')} className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors">
                                Browse Available Courses
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Courses;
